#!/usr/bin/env python3
import pandas as pd
import re
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.cleansing.common import extract_year, initialize_base_columns, reorder_cleansing_columns, clean_text


def clean_data():
    """재고 데이터를 로드하고 전처리하는 함수"""
    print("재고 데이터 로드 및 전처리 시작...")
    
    # 데이터 로드 및 정리
    df_raw = pd.read_excel("data/raw/재고리스트_현대.xlsx", sheet_name=None)
    df_list = []
    for sheet, df in df_raw.items():
        if "조건" not in sheet:
            df = df.assign(시트명=sheet)  # 시트명을 컬럼으로 추가
            df_list.append(df)
    df = pd.concat(df_list, ignore_index=True)
    df = df.dropna(subset=["가격"])
    
    # 컬럼 정리 - 올바른 컬럼 매핑
    df = df[["판매코드", "Unnamed: 1", "칼라코드", "Unnamed: 3", "요청", "재고", "차종", "옵션", "외/내장칼라", "Unnamed: 9", "가격", "시트명"]]
    df.columns = ["code_sales_a", "code_sales_b", "code_color_a", "code_color_b", "request", "stock", "trim_raw", "options", "color_exterior", "color_interior", "price_car_original", "model_raw"]  # type: ignore
    
    # 기본 필드들 초기화 (공통 함수 사용)
    df = initialize_base_columns(df, "현대")
    
    # 추가 필드들
    df["key_subsidy"] = ""
    df["price_total"] = ""
    df["price_tax"] = ""
    df["price_registration"] = ""
    df["subsidy_national"] = ""
    df["subsidy_lease"] = ""
    df["subsidy_tax"] = ""
    df["promotion"] = ""
    df["price_car_tax_pre"] = ""
    df["price_car_tax_post"] = ""
    
    # 클렌징 규칙 적용
    df = apply_cleansing_rules(df)
    
    # 시트명 컬럼 제거 (Raw_모델로 사용됨)
    # df = df.drop(columns=["시트명"])  # 시트명은 이미 Raw_모델로 사용됨
    
    # 컬럼 순서 재정렬
    column_order = [
        "code_sales_a", "code_sales_b", "code_color_a", "code_color_b", 
        "request", "stock", "company", "model_raw", "trim_raw", "key_subsidy", "options", "model", "trim", 
        "year", "fuel", "wheel_tire", "color_exterior", "color_interior", "price_total", "price_car_original", "price_car_tax_pre", "price_car_tax_post", "price_tax", "price_registration", "subsidy_national", "subsidy_lease", "subsidy_tax", "promotion"
    ]
    df = df[column_order]
    
    print(f"✅ 현대차 전처리 완료! {len(df)}개 차량 데이터")
    print(f"📊 컬럼 구성: {len(df.columns)}개 필드")  # type: ignore
    return df


def apply_cleansing_rules(df):
    """클렌징 규칙을 적용하는 함수"""
    
    # 1. model_raw에서 모델, 트림, 연식, 연료 추출
    for idx, row in df.iterrows():
        raw_model = str(row["model_raw"]) if pd.notna(row["model_raw"]) else ""
        raw_trim = str(row["trim_raw"]) if pd.notna(row["trim_raw"]) else ""
        sheet_name = str(row["model_raw"]) if pd.notna(row["model_raw"]) else ""
        
        # 모델 추출 (model_raw에서 특정 케이스 규칙에 따라 처리)
        df.at[idx, "model"] = extract_model_from_raw_model(raw_model)
        
        # 트림 추출 (모델별로 구분)
        df.at[idx, "trim"] = extract_trim_by_model(raw_trim, sheet_name)
        
        # 연료 추출
        df.at[idx, "fuel"] = extract_fuel(raw_trim)
        
        # 싼타페 하이브리드 조건 확인 (trim_raw에서 하이브리드 확인)
        if df.at[idx, "model"] == "싼타페" and "하이브리드" in raw_trim:
            df.at[idx, "model"] = "싼타페 하이브리드"
        
        # 연식 추출
        df.at[idx, "year"] = extract_year(raw_trim)
        
        # 휠&타이어 설정 (트림과 옵션 모두 체크)
        option_value = str(row["options"]) if pd.notna(row["options"]) else ""
        wheel_tire, cleaned_option = extract_wheel_tire_from_both(raw_trim, option_value)
        df.at[idx, "wheel_tire"] = wheel_tire
        df.at[idx, "options"] = cleaned_option
        
        # 보조금 트림 매칭
        df.at[idx, "key_subsidy"] = match_subsidy_trim(df.at[idx, "fuel"], df.at[idx, "model"], raw_trim)
        

    
    return df


def extract_model_from_raw_model(raw_model):
    """Raw_모델에서 특정 케이스 규칙에 따라 모델 정보를 추출하는 함수"""
    # 모델명 패턴 매칭
    model_patterns = [
        "팰리세이드", "싼타페", "아이오닉9", "아반떼", "캐스퍼"
    ]
    
    for pattern in model_patterns:
        if pattern in raw_model:
            return pattern
    
    return "?"


def extract_trim_by_model(raw_trim, sheet_name):
    """모델별로 트림 정보를 추출하는 함수"""
    # sheet_name에서 모델 정보 추출
    model = extract_model_from_raw_model(sheet_name)
    
    if model == "팰리세이드":
        trim_patterns = ["캘리그래피", "프레스티지", "익스클루시브"]
    elif model == "싼타페":
        trim_patterns = ["캘리그래피", "프레스티지 플러스", "프레스티지", "익스클루시브"]
    elif model == "아이오닉9":
        trim_patterns = ["CALLIGRAPHY", "PRESTIGE", "EXCLUSIVE"]
    elif model == "아반떼":
        trim_patterns = ["Modern", "Smart", "Inspiration", "N", "N Line", "하이브리드"]
    elif model == "캐스퍼":
        trim_patterns = ["인스퍼레이션"]
    else:
        return "?"
    
    for pattern in trim_patterns:
        if pattern in raw_trim:
            # 하이브리드의 경우 추가 구분
            if pattern == "하이브리드":
                if "Modern" in raw_trim:
                    return "하이브리드 모던"
                elif "Smart" in raw_trim:
                    return "하이브리드 스마트"
                elif "Inspiration" in raw_trim:
                    return "하이브리드 인스퍼레이션"
                elif "N Line" in raw_trim:
                    return "하이브리드 N-Line"
                else:
                    return "하이브리드"
            # 영문 트림을 한글로 변환
            elif pattern == "CALLIGRAPHY":
                return "캘리그래피"
            elif pattern == "PRESTIGE":
                return "프레스티지"
            elif pattern == "EXCLUSIVE":
                return "익스클루시브"
            elif pattern == "Modern":
                return "모던"
            elif pattern == "Smart":
                return "스마트"
            elif pattern == "Inspiration":
                return "인스퍼레이션"
            elif pattern == "N Line":
                return "N-Line"
            else:
                return pattern
    
    return "?"


def extract_fuel(raw_model):
    """연료 정보를 추출하는 함수"""
    if "전기모터" in raw_model:
        return "전기"
    elif "하이브리드" in raw_model:
        return "하이브리드"
    elif "가솔린" in raw_model:
        return "가솔린"
    else:
        return "?"


# extract_year 함수는 common.py로 이동됨


def extract_wheel_tire_from_both(raw_trim, option_value):
    """Raw_트림과 옵션에서 휠&타이어 정보를 추출하는 함수"""
    # Raw_트림에서 인치 패턴 찾기
    raw_trim_str = str(raw_trim) if pd.notna(raw_trim) else ""
    inch_pattern = re.search(r'(\d+)인치', raw_trim_str)
    if inch_pattern:
        # Raw_트림에서 휠&타이어 정보를 찾았으므로 옵션에서도 해당 정보 제거
        option_str = str(option_value) if pd.notna(option_value) else ""
        if "인치" in option_str:
            options = option_str.split(',')
            cleaned_options = []
            for option in options:
                option = option.strip()
                if "인치" not in option:  # 인치 관련 옵션 제외
                    cleaned_options.append(option)
            cleaned_option = ', '.join(cleaned_options).strip()
            return f"{inch_pattern.group(1)}인치 휠&타이어", cleaned_option
        return f"{inch_pattern.group(1)}인치 휠&타이어", option_value
    
    # 옵션에서 인치 패턴 찾기
    option_str = str(option_value) if pd.notna(option_value) else ""
    if "인치" in option_str:
        # 옵션을 쉼표로 분리해서 각각 체크
        options = option_str.split(',')
        cleaned_options = []
        wheel_tire = "기본 휠&타이어"  # 기본값 설정
        
        for option in options:
            option = option.strip()
            if "인치" in option:
                # 인치 패턴 추출
                inch_match = re.search(r'(\d+)인치', option)
                if inch_match:
                    wheel_tire = f"{inch_match.group(1)}인치 휠&타이어"
                else:
                    wheel_tire = option  # 인치 숫자가 없으면 전체 옵션 반환
            else:
                cleaned_options.append(option)
        
        if wheel_tire != "기본 휠&타이어":
            cleaned_option = ', '.join(cleaned_options).strip()
            return wheel_tire, cleaned_option
    
    return "기본 휠&타이어", option_value


def match_subsidy_trim(fuel_type, model, raw_trim):
    """보조금 트림 매칭 함수"""
    # 전기차가 아니면 "-" 반환
    if fuel_type != "전기":
        return "-"
    
    # 아이오닉9 매칭
    if model == "아이오닉9":
        raw_trim_str = str(raw_trim)
        
        # 성능형 AWD
        if "AWD(성능)" in raw_trim_str:
            return "아이오닉9 성능형 AWD"
        # 항속형 AWD
        elif "AWD(항속)" in raw_trim_str:
            return "아이오닉9 항속형 AWD"
        # 항속형 2WD
        elif "2WD" in raw_trim_str:
            return "아이오닉9 항속형 2WD"
        else:
            return "?"
    
    # 다른 전기차 모델이 있다면 여기에 추가
    return "?"


 
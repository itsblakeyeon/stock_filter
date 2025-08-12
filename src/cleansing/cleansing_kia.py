#!/usr/bin/env python3
import pandas as pd
import re
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.cleansing.common import (
    extract_year,
    initialize_base_columns,
    reorder_cleansing_columns,
    clean_text,
)


def extract_drive_and_seating(raw_trim):
    """구동방식과 인승 정보를 추출하는 함수"""
    drive_type = "2WD"
    if "AWD" in raw_trim:
        drive_type = "AWD"
    elif "4WD" in raw_trim:
        drive_type = "4WD"
    elif "2WD" in raw_trim:
        drive_type = "2WD"

    seating = ""
    if "6인승" in raw_trim:
        seating = "6인승"
    elif "7인승" in raw_trim:
        seating = "7인승"
    elif "9인승" in raw_trim:
        seating = "9인승"

    return drive_type, seating


def clean_data():
    """기아차 재고 데이터를 로드하고 전처리하는 함수"""
    df_raw = pd.read_excel("data/raw/재고리스트_기아.xls", sheet_name=None)
    df = df_raw["sheet1"]

    df = df.iloc[1:].reset_index(drop=True)
    df = df.dropna(subset=["가격"])

    df = df[
        [
            "판매코드",
            "Unnamed: 1",
            "칼라코드",
            "Unnamed: 3",
            "요청",
            "재고",
            "차종",
            "옵션",
            "외/내장칼라",
            "Unnamed: 9",
            "가격",
        ]
    ]
    df.columns = ["code_sales_a", "code_sales_b", "code_color_a", "code_color_b", "request", "stock", "model_raw", "options", "color_exterior", "color_interior", "price_car_original"]  # type: ignore

    df["trim_raw"] = ""

    # 기본 필드들 초기화 (공통 함수 사용)
    df = initialize_base_columns(df, "기아")

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

    df = apply_cleansing_rules(df)

    column_order = [
        "code_sales_a",
        "code_sales_b",
        "code_color_a",
        "code_color_b",
        "request",
        "stock",
        "company",
        "model_raw",
        "trim_raw",
        "key_subsidy",
        "options",
        "model",
        "trim",
        "year",
        "fuel",
        "wheel_tire",
        "color_exterior",
        "color_interior",
        "price_total",
        "price_car_original",
        "price_car_tax_pre",
        "price_car_tax_post",
        "price_tax",
        "price_registration",
        "subsidy_national",
        "subsidy_lease",
        "subsidy_tax",
        "promotion",
    ]
    df = df[column_order]

    print(f"✅ 기아차 전처리 완료! {len(df)}개 차량 데이터")
    print(f"📊 컬럼 구성: {len(df.columns)}개 필드")  # type: ignore
    return df


def apply_cleansing_rules(df):
    """기아차 클렌징 규칙을 적용하는 함수"""
    for idx, row in df.iterrows():
        raw_model = str(row["model_raw"]) if pd.notna(row["model_raw"]) else ""

        if "봉고" in raw_model:
            df.at[idx, "model"] = "봉고"
            df.at[idx, "trim_raw"] = raw_model.replace("봉고", "").strip()
        elif "EV4" in raw_model:
            df.at[idx, "model"] = "EV4"
            df.at[idx, "trim_raw"] = raw_model.replace("EV4", "").strip()
        elif "EV6" in raw_model:
            df.at[idx, "model"] = "EV6"
            df.at[idx, "trim_raw"] = raw_model.replace("EV6", "").strip()
        elif "EV9" in raw_model:
            df.at[idx, "model"] = "EV9"
            df.at[idx, "trim_raw"] = raw_model.replace("EV9", "").strip()
        elif "K5" in raw_model:
            df.at[idx, "model"] = "K5"
            df.at[idx, "trim_raw"] = raw_model.replace("K5", "").strip()
        elif "타스만" in raw_model:
            df.at[idx, "model"] = "타스만"
            df.at[idx, "trim_raw"] = raw_model.replace("타스만", "").strip()
        elif "니로" in raw_model:
            df.at[idx, "model"] = "니로"
            df.at[idx, "trim_raw"] = raw_model.replace("니로", "").strip()
        elif "EV3" in raw_model:
            df.at[idx, "model"] = "EV3"
            df.at[idx, "trim_raw"] = raw_model.replace("EV3", "").strip()
        elif "K8" in raw_model:
            df.at[idx, "model"] = "K8"
            df.at[idx, "trim_raw"] = raw_model.replace("K8", "").strip()
        elif "K9" in raw_model:
            df.at[idx, "model"] = "K9"
            df.at[idx, "trim_raw"] = raw_model.replace("K9", "").strip()
        elif "쏘렌토" in raw_model:
            df.at[idx, "model"] = "쏘렌토"
            df.at[idx, "trim_raw"] = raw_model.replace("쏘렌토", "").strip()
        elif "카니발" in raw_model:
            df.at[idx, "model"] = "카니발"
            df.at[idx, "trim_raw"] = raw_model.replace("카니발", "").strip()
        elif "1 1/4톤 샤시" in raw_model:
            df.at[idx, "model"] = "봉고"
            df.at[idx, "trim_raw"] = raw_model.replace("1 1/4톤 샤시", "").strip()
        else:
            df.at[idx, "model"] = "?"
            df.at[idx, "trim_raw"] = raw_model

    for idx, row in df.iterrows():
        raw_trim = str(row["trim_raw"]) if pd.notna(row["trim_raw"]) else ""
        raw_model = str(row["model_raw"]) if pd.notna(row["model_raw"]) else ""

        df.at[idx, "trim"] = extract_trim(raw_model, raw_trim)
        df.at[idx, "fuel"] = extract_fuel(raw_model)
        df.at[idx, "year"] = extract_year(raw_model)
        wheel_tire, cleaned_option = extract_wheel_tire(row["options"])
        df.at[idx, "wheel_tire"] = wheel_tire
        df.at[idx, "options"] = cleaned_option

        # key_subsidy 매핑
        df.at[idx, "key_subsidy"] = extract_subsidy_trim(
            raw_model, raw_trim, row["options"]
        )

    return df


def extract_trim(raw_model, raw_trim):
    """기아차 트림 정보를 추출하는 함수"""
    if "EV3" in raw_model:
        if "GT-Line" in raw_trim:
            if "롱레인지" in raw_trim:
                return "GT-Line 롱레인지"
            elif "스탠다드" in raw_trim:
                return "GT-Line"
            else:
                return "GT-Line"
        elif "어스" in raw_trim:
            if "스탠다드" in raw_trim:
                return "어스 스탠다드"
            elif "롱레인지" in raw_trim:
                return "어스 롱레인지"
            else:
                return "어스"
        elif "에어" in raw_trim:
            if "스탠다드" in raw_trim:
                return "에어 스탠다드"
            elif "롱레인지" in raw_trim:
                return "에어 롱레인지"
            else:
                return "에어"
        else:
            return "?"

    elif "EV4" in raw_model:
        if "GT-LINE" in raw_trim:
            if "롱레인지" in raw_trim:
                return "GT-Line 롱레인지"
            elif "스탠다드" in raw_trim:
                return "GT-Line"
            else:
                return "GT-Line"
        elif "어스" in raw_trim:
            if "스탠다드" in raw_trim:
                return "어스 스탠다드"
            elif "롱레인지" in raw_trim:
                return "어스 롱레인지"
            else:
                return "어스"
        elif "에어" in raw_trim:
            if "스탠다드" in raw_trim:
                return "에어 스탠다드"
            elif "롱레인지" in raw_trim:
                return "에어 롱레인지"
            else:
                return "에어"
        else:
            return "?"

    elif "EV6" in raw_model:
        if "GT-Line" in raw_trim:
            if "롱레인지" in raw_trim:
                return "GT-Line 롱레인지"
            else:
                return "GT-Line"
        elif "어스" in raw_trim:
            if "롱레인지" in raw_trim:
                return "어스 롱레인지"
            elif "스탠다드" in raw_trim:
                return "어스 스탠다드"
            else:
                return "어스"
        elif "에어" in raw_trim:
            if "롱레인지" in raw_trim:
                return "에어 롱레인지"
            else:
                return "에어"
        elif "라이트" in raw_trim:
            if "롱레인지" in raw_trim:
                return "라이트 롱레인지"
            else:
                return "라이트"
        else:
            return "?"

    elif "EV9" in raw_model:
        if "GT" in raw_trim:
            return "GT"
        elif "GT-Line" in raw_trim:
            if "롱레인지" in raw_trim:
                return "GT-Line 롱레인지"
            else:
                return "GT-Line"
        elif "어스" in raw_trim:
            if "롱레인지" in raw_trim:
                return "어스 롱레인지"
            elif "스탠다드" in raw_trim:
                return "어스 스탠다드"
            else:
                return "어스"
        elif "에어" in raw_trim:
            if "롱레인지" in raw_trim:
                return "에어 롱레인지"
            elif "스탠다드" in raw_trim:
                return "에어 스탠다드"
            else:
                return "에어"
        else:
            return "?"

    elif "K5" in raw_model:
        if "프레스티지" in raw_trim:
            return "프레스티지"
        elif "모던" in raw_trim:
            return "모던"
        elif "스마트" in raw_trim:
            return "스마트"
        elif "노블레스" in raw_trim:
            return "노블레스"
        elif "시그니처" in raw_trim:
            return "시그니처"
        elif "베스트셀렉션" in raw_trim:
            return "베스트셀렉션"
        elif "스마트셀렉션" in raw_trim:
            return "스마트셀렉션"
        elif "트렌디" in raw_trim:
            return "트렌디"
        else:
            return "?"

    elif "봉고" in raw_model:
        return "-"

    elif "모닝" in raw_model:
        if "인터스티어" in raw_trim:
            return "인터스티어"
        elif "프리미엄" in raw_trim:
            return "프리미엄"
        else:
            return "?"

    elif "K3" in raw_model:
        if "프리미엄" in raw_trim:
            return "프리미엄"
        elif "모던" in raw_trim:
            return "모던"
        else:
            return "?"

    elif "K8" in raw_model:
        if "프리미엄" in raw_trim:
            return "프리미엄"
        elif "모던" in raw_trim:
            return "모던"
        elif "노블레스" in raw_trim:
            return "노블레스"
        else:
            return "?"

    elif "타스만" in raw_model:
        return "-"

    elif "니로" in raw_model:
        return "-"

    elif "스포티지" in raw_model:
        drive_type, seating = extract_drive_and_seating(raw_trim)
        if "프리미엄" in raw_trim:
            return f"프리미엄 {drive_type} {seating}"
        elif "모던" in raw_trim:
            return f"모던 {drive_type} {seating}"
        else:
            return "?"

    elif "쏘렌토" in raw_model:
        if "가솔린 2.5T" in raw_model and "노블레스" in raw_trim:
            return "가솔린 터보 2.5 노블레스"
        elif "가솔린 2.5T" in raw_model and "시그니처" in raw_trim:
            return "가솔린 터보 2.5 시그니처"
        elif "가솔린 2.5T" in raw_model and "X-Line" in raw_trim:
            return "가솔린 터보 2.5 X-Line"
        elif "디젤 2.2" in raw_model and "프레스티지" in raw_trim:
            return "디젤 2.2 프레스티지"
        elif "하이브리드 1.6" in raw_model and "노블레스" in raw_trim:
            return "하이브리드 1.6 노블레스"
        else:
            return "?"

    elif "모하비" in raw_model:
        drive_type, seating = extract_drive_and_seating(raw_trim)
        if "프리미엄" in raw_trim:
            return f"프리미엄 {drive_type} {seating}"
        elif "모던" in raw_trim:
            return f"모던 {drive_type} {seating}"
        else:
            return "?"

    elif "카니발" in raw_model:
        if "가솔린 3.5" in raw_model and "시그니처" in raw_trim:
            return "가솔린 3.5 시그니처"
        elif (
            "하이브리드 1.6" in raw_model
            and "그래비티" in raw_trim
            and "7인승" in raw_trim
        ):
            return "하이브리드 1.6 그래비티 7인승"
        elif (
            "하이브리드 1.6" in raw_model
            and "그래비티" in raw_trim
            and "9인승" in raw_trim
        ):
            return "하이브리드 1.6 그래비티 9인승"
        elif (
            "하이브리드 1.6" in raw_model
            and "노블레스" in raw_trim
            and "7인승" in raw_trim
        ):
            return "하이브리드 1.6 노블레스 7인승"
        elif (
            "하이브리드 1.6" in raw_model
            and "노블레스" in raw_trim
            and "9인승" in raw_trim
        ):
            return "하이브리드 1.6 노블레스 9인승"
        else:
            return "?"

    else:
        return "?"


def extract_fuel(raw_trim):
    """연료 정보를 추출하는 함수"""
    if "LPI" in raw_trim.upper():
        return "LPI"
    elif "전기모터" in raw_trim or "EV" in raw_trim:
        return "전기"
    elif "LPG" in raw_trim:
        return "LPG"
    elif "하이브리드" in raw_trim or "HEV" in raw_trim:
        return "하이브리드"
    elif "가솔린" in raw_trim or "T/GDI" in raw_trim or "GSL" in raw_trim:
        return "가솔린"
    else:
        return "?"


# extract_year 함수는 common.py로 이동됨


def extract_wheel_tire(option_value):
    """휠&타이어 정보를 추출하는 함수"""
    import re

    option_str = str(option_value) if pd.notna(option_value) else ""
    if "인치" in option_str:
        # 옵션을 쉼표로 분리해서 각각 체크
        options = option_str.split(",")
        cleaned_options = []
        wheel_found = False
        wheel_tire = "기본 휠&타이어"  # 기본값 설정

        for option in options:
            option = option.strip()
            if "인치" in option:
                wheel_found = True
                # 인치 패턴 추출
                inch_match = re.search(r"(\d+)인치", option)
                if inch_match:
                    wheel_tire = f"{inch_match.group(1)}인치"
                else:
                    wheel_tire = option  # 인치 숫자가 없으면 전체 옵션 반환
            else:
                cleaned_options.append(option)

        if wheel_found:
            cleaned_option = ", ".join(cleaned_options).strip()
            return wheel_tire, cleaned_option

    return "기본 휠&타이어", option_value


def extract_subsidy_trim(raw_model, raw_trim, option_value):
    """보조금 트림 정보를 추출하는 함수"""
    # 연료가 전기가 아니면 "-" 반환
    if "전기" not in raw_model and "EV" not in raw_model:
        return "-"

    # EV3 모델 처리
    if "EV3" in raw_model:
        option_str = str(option_value) if pd.notna(option_value) else ""

        if "롱레인지" in raw_trim:
            if "19인치휠" in option_str:
                return "EV3 롱레인지 2WD 19인치"
            else:
                return "EV3 롱레인지 2WD 17인치"
        elif "스탠다드" in raw_trim:
            return "EV3 스탠다드 2WD"
        else:
            return "?"

    # EV4 모델 처리
    elif "EV4" in raw_model:
        option_str = str(option_value) if pd.notna(option_value) else ""

        if "롱레인지" in raw_trim:
            if "GT-LINE" in raw_trim:
                return "EV4 롱레인지 GTL 2WD 19인치"
            elif "19인치휠" in option_str:
                return "EV4 롱레인지 2WD 19인치"
            else:
                return "EV4 롱레인지 2WD 17인치"
        elif "스탠다드" in raw_trim:
            if "19인치휠" in option_str:
                return "EV4 스탠다드 2WD 19인치"
            else:
                return "EV4 스탠다드 2WD 17인치"
        else:
            return "?"

    # EV6 모델 처리
    elif "EV6" in raw_model:
        if "GT" in raw_trim:
            return "더뉴EV6 GT"
        elif "롱레인지" in raw_trim:
            if "4WD" in raw_trim:
                if "20인치" in raw_trim or "20인치" in str(option_value):
                    return "더뉴EV6 롱레인지 4WD 20인치"
                else:
                    return "더뉴EV6 롱레인지 4WD 19인치"
            else:  # 2WD
                if "20인치" in raw_trim or "20인치" in str(option_value):
                    return "더뉴EV6 롱레인지 2WD 20인치"
                else:
                    return "더뉴EV6 롱레인지 2WD 19인치"
        else:  # 스탠다드
            return "더뉴EV6 스탠다드"

    # EV9 모델 처리
    elif "EV9" in raw_model:
        if "GT" in raw_trim:
            return "EV9 롱레인지 GTL 4WD 21인치"
        elif "롱레인지" in raw_trim:
            if "4WD" in raw_trim:
                if "21인치" in raw_trim or "21인치" in str(option_value):
                    return "EV9 롱레인지 4WD 21인치"
                else:
                    return "EV9 롱레인지 4WD 19인치"
            else:  # 2WD
                if "20인치" in raw_trim or "20인치" in str(option_value):
                    return "EV9 롱레인지 2WD 20인치"
                else:
                    return "EV9 롱레인지 2WD 19인치"
        else:  # 스탠다드
            return "EV9 스탠다드"

    # 니로 모델 처리
    elif "니로" in raw_model:
        return "The all-new Kia Niro EV"

    # 레이 모델 처리
    elif "레이" in raw_model:
        if "밴" in raw_trim:
            if "2인승" in raw_trim:
                return "레이 EV 2WD 14인치 2인승 밴"
            else:
                return "레이 EV 2WD 14인치 1인승 밴"
        else:
            return "레이 EV 2WD 14인치 4인승 승용"

    # 기타 전기차는 "?" 반환
    else:
        return "?"

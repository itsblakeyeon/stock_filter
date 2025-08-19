#!/usr/bin/env python3
"""
가격 참조 데이터 모듈
price_reference.xlsx에서 보조금과 가격 데이터를 로드
"""

import pandas as pd
import os


def load_price_reference_data():
    """통합 가격 참조 데이터를 엑셀 파일에서 로드하는 함수"""
    try:
        # Pricing 폴더 기준으로 data 폴더 찾기
        pricing_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(pricing_dir, "data", "price_reference.xlsx")
        
        if os.path.exists(file_path):
            # 보조금 데이터 로드
            subsidy_df = pd.read_excel(file_path, sheet_name='보조금')
            
            # 가격 데이터 로드 (있는 경우)
            try:
                price_df = pd.read_excel(file_path, sheet_name='가격표')
            except:
                price_df = pd.DataFrame()
            
            # 통합 요약 데이터 로드 (있는 경우)
            try:
                summary_df = pd.read_excel(file_path, sheet_name='통합_요약')
            except:
                summary_df = pd.DataFrame()
            
            return {
                'subsidy': subsidy_df,
                'price': price_df,
                'summary': summary_df
            }
        else:
            print(f"⚠️ 가격 참조 데이터 파일을 찾을 수 없습니다: {file_path}")
            return {
                'subsidy': pd.DataFrame(),
                'price': pd.DataFrame(),
                'summary': pd.DataFrame()
            }
    except Exception as e:
        print(f"❌ 가격 참조 데이터 로드 실패: {e}")
        return {
            'subsidy': pd.DataFrame(),
            'price': pd.DataFrame(),
            'summary': pd.DataFrame()
        }


def get_subsidy_data():
    """보조금 데이터를 반환하는 함수"""
    data = load_price_reference_data()
    return data['subsidy']


def get_price_data():
    """가격 데이터를 반환하는 함수"""
    data = load_price_reference_data()
    return data['price']


def get_all_subsidy_data():
    """모든 보조금 데이터를 반환하는 함수"""
    return get_subsidy_data()


def get_subsidy_info(key_subsidy: str, fuel_type: str = ""):
    """
    보조금 키로 보조금 정보를 조회하는 함수
    
    Args:
        key_subsidy: 보조금 키 (예: "아이오닉9 성능형 AWD")
        fuel_type: 연료 타입 (선택사항)
    
    Returns:
        dict: 보조금 정보 또는 기본값
    """
    subsidy_df = get_subsidy_data()
    
    if subsidy_df.empty:
        return {
            'subsidy_national': 0,
            'subsidy_lease': 0,
            'subsidy_tax': 0
        }
    
    # key_subsidy로 매칭 시도
    if 'key_subsidy' in subsidy_df.columns:
        matches = subsidy_df[subsidy_df['key_subsidy'] == key_subsidy]
        if not matches.empty:
            row = matches.iloc[0]
            return {
                'subsidy_national': row.get('subsidy_national', 0),
                'subsidy_lease': row.get('subsidy_lease', 0),
                'subsidy_tax': row.get('subsidy_tax', 0)
            }
    
    # 전기차의 경우 세금 보조금 적용
    if fuel_type == "전기":
        return {
            'subsidy_national': 0,
            'subsidy_lease': 0,
            'subsidy_tax': 1400000  # 전기차 세금 보조금
        }
    
    return {
        'subsidy_national': 0,
        'subsidy_lease': 0,
        'subsidy_tax': 0
    }


def get_price_info(model: str, trim: str = "", year: str = ""):
    """
    모델/트림 정보로 가격 정보를 조회하는 함수
    
    Args:
        model: 모델명
        trim: 트림명 (선택사항)
        year: 연식 (선택사항)
    
    Returns:
        dict: 가격 정보 또는 기본값
    """
    price_df = get_price_data()
    
    if price_df.empty:
        return {
            'price_car_original': 0,
            'price_options': 0
        }
    
    # 모델로 매칭 시도
    if 'model' in price_df.columns:
        matches = price_df[price_df['model'] == model]
        
        # 트림으로 추가 필터링
        if not matches.empty and trim and 'trim' in price_df.columns:
            trim_matches = matches[matches['trim'] == trim]
            if not trim_matches.empty:
                matches = trim_matches
        
        if not matches.empty:
            row = matches.iloc[0]
            return {
                'price_car_original': row.get('price_car_original', 0),
                'price_options': row.get('price_options', 0)
            }
    
    return {
        'price_car_original': 0,
        'price_options': 0
    }
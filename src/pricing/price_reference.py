#!/usr/bin/env python3
"""
통합 가격 참조 데이터 모듈
price_reference.xlsx에서 보조금과 가격 데이터를 로드
"""

import pandas as pd
import os

def load_price_reference_data():
    """통합 가격 참조 데이터를 엑셀 파일에서 로드하는 함수"""
    try:
        file_path = "../Pricing/data/price_reference.xlsx"
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
    """보조금 데이터만 반환하는 함수"""
    data = load_price_reference_data()
    return data['subsidy']

def get_price_data():
    """가격 데이터만 반환하는 함수"""
    data = load_price_reference_data()
    return data['price']

def get_summary_data():
    """통합 요약 데이터만 반환하는 함수"""
    data = load_price_reference_data()
    return data['summary']

def find_subsidy_by_trim(company, trim):
    """회사와 트림으로 보조금 정보를 찾는 함수"""
    subsidy_df = get_subsidy_data()
    if subsidy_df.empty:
        return None
    
    # 정확한 매칭 시도
    match = subsidy_df[
        (subsidy_df['company'] == company) & 
        (subsidy_df['trim'] == trim)
    ]
    
    if not match.empty:
        return match.iloc[0].to_dict()
    
    # 부분 매칭 시도 (트림 이름에 포함된 경우)
    match = subsidy_df[
        (subsidy_df['company'] == company) & 
        (subsidy_df['trim'].str.contains(trim, na=False))
    ]
    
    if not match.empty:
        return match.iloc[0].to_dict()
    
    return None

def find_price_by_trim(model_info, trim, year=None):
    """모델, 트림, 연식으로 가격 정보를 찾는 함수 (정확한 매칭만)"""
    price_df = get_price_data()
    if price_df.empty:
        return None
    
    # 정확한 매칭만 시도 (모델 + 트림 + 연식)
    if year is not None:
        match = price_df[
            (price_df['model'] == model_info) & 
            (price_df['trim'] == trim) & 
            (price_df['year'] == year)
        ]
        if not match.empty:
            return match.iloc[0].to_dict()
    
    return None


def find_price_by_key(key):
    """Key 필드로 가격 정보를 찾는 함수"""
    price_df = get_price_data()
    if price_df.empty:
        return None
    
    # Key 필드로 정확한 매칭 시도
    match = price_df[price_df['Key'] == key]
    if not match.empty:
        return match.iloc[0].to_dict()
    
    return None

def get_all_subsidy_data():
    """기존 코드와의 호환성을 위한 함수 (subsidy.py의 data 변수와 동일)"""
    subsidy_df = get_subsidy_data()
    if not subsidy_df.empty:
        return subsidy_df[['company', 'trim', 'subsidy_national', 'subsidy_lease']].values.tolist()
    return []

def get_all_price_data():
    """가격 데이터를 리스트 형태로 반환하는 함수"""
    price_df = get_price_data()
    if not price_df.empty:
        return price_df.values.tolist()
    return []

# 기존 코드와의 호환성을 위한 변수들 (프로그램 시작시 한번만 로드)
_data_cache = {}

def get_cached_data():
    """캐시된 데이터 반환 (성능 최적화)"""
    global _data_cache
    if not _data_cache:
        _data_cache = {
            'subsidy_data': get_all_subsidy_data(),
            'price_data': get_all_price_data(),
            'subsidy_df': get_subsidy_data(),
            'price_df': get_price_data(),
            'summary_df': get_summary_data()
        }
    return _data_cache

# 기존 코드와의 호환성 유지
subsidy_data = get_all_subsidy_data()
subsidy_df = get_subsidy_data()


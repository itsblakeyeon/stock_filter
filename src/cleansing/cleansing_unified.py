#!/usr/bin/env python3
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.cleansing.cleansing_hyundai import clean_data as clean_hyundai_data
from src.cleansing.cleansing_kia import clean_data as clean_kia_data
from src.cleansing.common import reorder_cleansing_columns


def apply_common_cleansing(df):
    """기본 클렌징 로직을 적용하는 함수"""
    print("🔧 최종 컬럼 순서 정렬 중...")

    # 공통 함수 사용하여 컬럼 순서 정렬
    df = reorder_cleansing_columns(df)

    print("✅ 기본 클렌징 로직 완료!")
    return df


def clean_all_data():
    """현대차와 기아차 데이터를 모두 클렌징하고 통합하는 함수"""
    print("🚗 현대차 + 기아차 통합 클렌징 시작...")
    
    # 1. 현대차 데이터 클렌징 (개별 처리)
    print("\n📋 현대차 데이터 처리 중...")
    hyundai_df = clean_hyundai_data()
    
    # 2. 기아차 데이터 클렌징 (개별 처리)
    print("\n📋 기아차 데이터 처리 중...")
    kia_df = clean_kia_data()
    
    # 3. 데이터 통합
    print("\n🔗 데이터 통합 중...")
    combined_df = pd.concat([hyundai_df, kia_df], ignore_index=True)
    
    # 4. Key 컬럼 추가 (company_model_trim_year)
    combined_df["key_admin"] = combined_df["company"] + "_" + combined_df["model"] + "_" + combined_df["trim"] + "_" + combined_df["year"]
    
    # 5. 공통 클렌징 로직 적용 (보조금 매칭, 비용 계산, 가격 매칭)
    combined_df = apply_common_cleansing(combined_df)
    
    print(f"\n✅ 통합 클렌징 완료!")
    print(f"📊 현대차: {len(hyundai_df)}대")
    print(f"📊 기아차: {len(kia_df)}대")
    print(f"📊 총합: {len(combined_df)}대")
    print(f"📋 컬럼 구성: {len(combined_df.columns)}개 필드")  # type: ignore
    print(f"🏷️ 회사별 분포: {combined_df['company'].value_counts().to_dict()}")  # type: ignore
    
    return combined_df



#!/usr/bin/env python3
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.pricing.pricing import add_subsidy_columns_to_df, add_price_columns_to_df, calculate_pricing


def apply_pricing(df):
    """모든 가격 관련 계산을 적용하는 함수 - calculate_pricing을 직접 호출"""
    return calculate_pricing(df)


def main(cleaned_df):
    """프라이싱 메인 함수"""
    print("🚗 가격 계산 시작...")
    
    # 모든 가격 관련 계산 적용
    priced_df = apply_pricing(cleaned_df)
    
    print(f"✅ 가격 계산 완료: {len(priced_df)}대 차량")
    return priced_df



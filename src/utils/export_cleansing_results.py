#!/usr/bin/env python3
"""
클렌징 결과 내보내기 유틸리티
"""

import pandas as pd
import os


def remove_korean_subsidy_columns(df):
    """한국어 보조금 컬럼들을 제거하는 함수"""
    korean_columns = ["보조금_국비", "보조금_리스", "보조금_세금"]
    
    # 제거할 컬럼들 확인
    columns_to_remove = [col for col in korean_columns if col in df.columns]
    
    if columns_to_remove:
        print(f"🗑️ 한국어 보조금 컬럼 제거: {columns_to_remove}")
        df = df.drop(columns=columns_to_remove)
    
    return df


def export_cleansing_results(df):
    """클렌징된 데이터를 엑셀 파일로 내보내는 함수"""
    print("📤 클렌징 결과 내보내기 시작...")
    
    # 한국어 보조금 컬럼 제거
    df = remove_korean_subsidy_columns(df)
    
    # 내보내기 디렉토리 확인
    export_dir = "data/export"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # 파일명
    filename = os.path.join(export_dir, "cleansing_stock_unified.xlsx")
    
    # 엑셀 파일로 저장
    df.to_excel(filename, index=False)
    
    print(f"✅ 클렌징 결과 내보내기 완료!")
    print(f"📁 파일 위치: {filename}")
    print(f"📊 차량 수: {len(df)}대")
    print(f"📋 컬럼 수: {len(df.columns)}개")
    
    return df 
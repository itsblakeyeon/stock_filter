#!/usr/bin/env python3
"""
통합 실행 스크립트
클렌징 → 리스팅 → 내보내기 순서로 실행
"""

import sys
import os
from datetime import datetime

# src 폴더를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.cleansing.cleansing_unified import clean_all_data
from src.pricing.pricing_unified import main as pricing_main
from src.listing.listing_unified import main as listing_main
from src.utils.export_cleansing_results import export_cleansing_results
from src.config.constants import FINAL_COLUMN_ORDER, DataProcessing


def main():
    print("🚗 재고 데이터 통합 처리 시작")
    print("=" * 60)

    # 현재 날짜 가져오기 (YYYYMMDD 형식)
    current_date = datetime.now().strftime("%y%m%d")

    # 1. 통합 클렌징
    print(f"\n📋 1단계: 통합 클렌징 시작...")
    cleaned_df = clean_all_data()
    print(f"✅ 클렌징 완료: {len(cleaned_df)}대")

    # 2. 통합 프라이싱
    print(f"\n📋 2단계: 통합 프라이싱 시작...")
    priced_df = pricing_main(cleaned_df)
    print(f"✅ 프라이싱 완료: {len(priced_df)}대")

    # 3. 통합 리스팅 (프라이싱된 데이터 사용)
    print(f"\n📋 3단계: 통합 리스팅 시작...")
    listing_main(priced_df)
    print(f"✅ 리스팅 완료")

    # 4. 내보내기 (클렌징된 데이터 사용)
    print(f"\n📋 4단계: 결과 내보내기 시작...")
    export_cleansing_results(cleaned_df)
    print(f"✅ 내보내기 완료")

    # 5. 최종 결과 파일 생성 (날짜 포함)
    create_final_result_file(current_date)

    print(f"\n🎉 모든 처리 완료!")
    print(f"📅 처리 날짜: {current_date}")
    print(
        f"📁 선택된 결과: stock_selected_{current_date}.xlsx (재고 {DataProcessing.STOCK_THRESHOLD} 이상)"
    )
    print(f"📁 전체 결과: stock_all_{current_date}.xlsx (전체 차량)")
    print(f"📁 업로드 결과: stock_upload_{current_date}.xlsx (필터링+선택 컬럼)")


def reorder_columns(df):
    """칼럼 순서 조정"""
    current_columns = list(df.columns)
    existing_order = [col for col in FINAL_COLUMN_ORDER if col in current_columns]
    remaining_columns = [col for col in current_columns if col not in existing_order]
    final_order = existing_order + remaining_columns
    return df[final_order]


def create_selected_file(date_str):
    """선택된 결과 파일 생성 (재고 조건 이상)"""
    import pandas as pd
    from src.config.constants import FilePaths

    listing_file = FilePaths.LISTING_UNIFIED
    if not os.path.exists(listing_file):
        print(f"❌ 리스팅 결과 파일을 찾을 수 없습니다: {listing_file}")
        return False

    df_selected = pd.read_excel(listing_file)
    df_selected = reorder_columns(df_selected)

    selected_filename = f"stock_selected_{date_str}.xlsx"
    df_selected.to_excel(selected_filename, index=False)
    print(f"✅ 선택된 결과 파일 생성: {selected_filename}")
    print(
        f"📊 선택된 차량: {len(df_selected)}대 (재고 {DataProcessing.STOCK_THRESHOLD} 이상), {len(df_selected.columns)}개 컬럼"
    )
    return True


def process_final_data(df_final):
    """최종 데이터 처리 (이미지, 가격, 보조금 컬럼 정리)"""
    from src.image.image import add_image_urls
    from src.pricing.pricing import calculate_pricing
    from src.utils.export_cleansing_results import remove_korean_subsidy_columns

    # 이미지 URL 추가
    df_final = add_image_urls(df_final)

    # 구독료 계산
    df_final = calculate_pricing(df_final)

    # 한국어 보조금 컬럼 제거
    df_final = remove_korean_subsidy_columns(df_final)

    # 칼럼 순서 조정 적용
    df_final = reorder_columns(df_final)

    return df_final


def create_all_file(date_str):
    """전체 결과 파일 생성 (전체 차량)"""
    import pandas as pd
    from src.config.constants import FilePaths

    unified_file = FilePaths.CLEANSING_UNIFIED
    if not os.path.exists(unified_file):
        print(f"❌ 통합 클렌징 결과 파일을 찾을 수 없습니다: {unified_file}")
        return False

    df_all = pd.read_excel(unified_file)
    df_all = process_final_data(df_all)

    all_filename = f"stock_all_{date_str}.xlsx"
    df_all.to_excel(all_filename, index=False)
    print(f"✅ 전체 결과 파일 생성: {all_filename}")
    print(f"📊 전체 차량: {len(df_all)}대, {len(df_all.columns)}개 컬럼")
    return True


def create_upload_file(date_str):
    """업로드용 컬럼으로 구성된 파일 생성 (필터링된 데이터)"""
    import pandas as pd
    from src.config.constants import FilePaths

    listing_file = FilePaths.LISTING_UNIFIED
    if not os.path.exists(listing_file):
        print(f"❌ 리스팅 결과 파일을 찾을 수 없습니다: {listing_file}")
        return False

    df_upload = pd.read_excel(listing_file)

    # 선택된 컬럼만 추출
    selected_columns = [
        "image_thumbnail",
        "image_detail",  # 7-8
        "company",
        "model",
        "trim",
        "year",
        "fuel",
        "options",
        "wheel_tire",
        "color_exterior",
        "color_interior",  # 13-21
        "fee_list",
        "fee_care",  # 33-34
        "fee_return_options_12m",
        "fee_return_options_36m",
        "fee_return_options_60m",
        "fee_return_options_84m",  # 47-50
        "fee_purchase_options_12m",
        "fee_purchase_options_36m",
        "fee_purchase_options_60m",
        "fee_purchase_options_84m",  # 51-54
    ]

    # 존재하는 컬럼만 선택
    available_columns = [col for col in selected_columns if col in df_upload.columns]
    df_upload = df_upload[available_columns]

    upload_filename = f"stock_upload_{date_str}.xlsx"
    df_upload.to_excel(upload_filename, index=False)
    print(f"✅ 업로드 결과 파일 생성: {upload_filename}")
    print(f"📊 필터링된 차량: {len(df_upload)}대, {len(df_upload.columns)}개 컬럼")
    return True


def create_final_result_file(date_str):
    """날짜가 붙은 최종 결과 파일 생성"""
    print(f"\n📋 5단계: 최종 결과 파일 생성...")

    # 선택된 파일 생성 (재고 조건 이상)
    if create_selected_file(date_str):
        # 전체 파일 생성 (전체 차량)
        create_all_file(date_str)
        # 업로드 파일 생성
        create_upload_file(date_str)


if __name__ == "__main__":
    main()

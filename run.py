#!/usr/bin/env python3
"""
통합 실행 스크립트
클렌징 → 리스팅 → 내보내기 순서로 실행
"""

import sys
import os

# src 폴더를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.cleansing.cleansing_unified import clean_all_data
from src.pricing.pricing_unified import main as pricing_main
from src.listing.listing_unified import main as listing_main
from src.config.constants import (
    FINAL_COLUMN_ORDER,
    get_today_date_string,
    set_global_date,
)


def get_date_input():
    """사용자로부터 날짜를 입력받는 함수"""
    today = get_today_date_string()

    print(f"\n📅 데이터 날짜 선택")
    print(f"현재 날짜: {today}")
    print("=" * 40)

    while True:
        try:
            user_input = input(
                f"사용할 날짜를 입력하세요 (YYMMDD 형식, 엔터 = 오늘날짜 {today}): "
            ).strip()
        except EOFError:
            # 입력이 없으면 기본값(오늘 날짜) 사용
            print(f"\n기본값 사용: {today}")
            return today

        if not user_input:  # 엔터만 누른 경우
            return today

        # 입력 형식 검증
        if len(user_input) == 6 and user_input.isdigit():
            # 날짜 유효성 간단 체크
            try:
                month = int(user_input[2:4])
                day = int(user_input[4:6])
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return user_input
                else:
                    print("❌ 잘못된 월/일입니다. 다시 입력해주세요.")
            except ValueError:
                print("❌ 잘못된 형식입니다. YYMMDD 형식으로 입력해주세요.")
        else:
            print("❌ YYMMDD 형식(6자리 숫자)으로 입력해주세요. 예: 250819")


def check_files_exist(date_str):
    """해당 날짜의 파일들이 존재하는지 확인"""
    from src.config.constants import FilePaths
    import os

    hyundai_file = FilePaths.get_hyundai_raw_file(date_str)
    kia_file = FilePaths.get_kia_raw_file(date_str)

    missing_files = []
    if not os.path.exists(hyundai_file):
        missing_files.append(hyundai_file)
    if not os.path.exists(kia_file):
        missing_files.append(kia_file)

    if missing_files:
        print(f"\n❌ 다음 파일들을 찾을 수 없습니다:")
        for file in missing_files:
            print(f"   - {file}")

        retry = input("\n다른 날짜를 선택하시겠습니까? (y/n): ").strip().lower()
        return retry == "y"

    print(f"✅ 필요한 파일들이 모두 존재합니다:")
    print(f"   - {hyundai_file}")
    print(f"   - {kia_file}")
    return True


def main():
    print("🚗 재고 데이터 통합 처리 시작")
    print("=" * 60)
    print(f"🔍 현재 작업 디렉토리: {os.getcwd()}")
    print(f"🔍 스크립트 위치: {os.path.abspath(__file__)}")
    print(f"🔍 스크립트 디렉토리: {os.path.dirname(os.path.abspath(__file__))}")

    # 파일 존재 여부 직접 확인
    print("🔍 파일 확인:")
    files_to_check = [
        "data/reference/price_reference.xlsx",
        "data/raw/재고리스트_현대_250819.xlsx",
        "data/raw/재고리스트_기아_250819.xls",
    ]
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        abs_path = os.path.abspath(file_path)
        print(f"   {file_path}: {'✅' if exists else '❌'} -> {abs_path}")
    print("=" * 60)

    # 날짜 선택
    while True:
        selected_date = get_date_input()
        if check_files_exist(selected_date):
            break

    # 선택한 날짜를 전역으로 설정
    set_global_date(selected_date)
    current_date = selected_date

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
    listed_df = listing_main(priced_df)
    print(f"✅ 리스팅 완료")

    # 4. 최종 결과 파일 생성 (날짜 포함)
    create_final_result_file(current_date, cleaned_df, listed_df)

    print(f"\n🎉 모든 처리 완료!")
    print(f"📅 처리 날짜: {current_date}")
    print(f"📁 결과 폴더: results/")
    print(f"   - stock_selected_{current_date}.xlsx (재고 3개 이상)")
    print(f"   - stock_all_{current_date}.xlsx (전체 차량)")
    print(f"   - stock_upload_{current_date}.xlsx (필터링+선택 컬럼)")


def reorder_columns(df):
    """칼럼 순서 조정"""
    current_columns = list(df.columns)
    existing_order = [col for col in FINAL_COLUMN_ORDER if col in current_columns]
    remaining_columns = [col for col in current_columns if col not in existing_order]
    final_order = existing_order + remaining_columns
    return df[final_order]


def create_selected_file(date_str, listed_df):
    """선택된 결과 파일 생성 (재고 3개 이상) - 무옵션/빌트인 캠 별도 시트"""
    from src.config.constants import FilePaths
    import pandas as pd

    # 재고 3개 이상 필터링
    df_filtered = (
        listed_df[listed_df["stock"] >= 3].copy()
        if "stock" in listed_df.columns
        else listed_df.copy()
    )
    df_selected = reorder_columns(df_filtered)

    # 무옵션과 빌트인 캠으로 분리 (정확한 빌트인캠 옵션만)
    df_no_options = df_selected[df_selected["options"] == "무옵션"].copy()

    def is_pure_builtin_cam(option_str):
        if pd.isna(option_str) or str(option_str).strip() in ["", "무옵션"]:
            return False
        option_str = str(option_str).strip()
        return option_str in ["빌트인캠", "빌트인 캠 패키지", "빌트인캠2"]

    df_builtin_cam = df_selected[
        df_selected["options"].apply(is_pure_builtin_cam)
    ].copy()

    selected_filename = FilePaths.get_results_file("selected", date_str)

    # ExcelWriter를 사용하여 여러 시트로 저장
    with pd.ExcelWriter(selected_filename, engine="openpyxl") as writer:
        if not df_no_options.empty:
            df_no_options.to_excel(writer, sheet_name="무옵션", index=False)
        if not df_builtin_cam.empty:
            df_builtin_cam.to_excel(writer, sheet_name="빌트인캠", index=False)

        # 전체 데이터도 별도 시트로 추가
        df_selected.to_excel(writer, sheet_name="전체", index=False)

    print(f"✅ 선택된 결과 파일 생성: {selected_filename}")
    print(
        f"📊 전체: {len(df_selected)}대 (재고 3개 이상), 무옵션: {len(df_no_options)}대, 빌트인캠: {len(df_builtin_cam)}대"
    )
    print(f"📊 컬럼 수: {len(df_selected.columns)}개")
    return True


def remove_korean_subsidy_columns(df):
    """한국어 보조금 컬럼들을 제거하는 함수"""
    korean_columns = ["보조금_국비", "보조금_리스", "보조금_세금"]

    # 제거할 컬럼들 확인
    columns_to_remove = [col for col in korean_columns if col in df.columns]

    if columns_to_remove:
        print(f"🗑️ 한국어 보조금 컬럼 제거: {columns_to_remove}")
        df = df.drop(columns=columns_to_remove)

    return df


def process_final_data(df_final):
    """최종 데이터 처리 (이미지, 가격, 보조금 컬럼 정리)"""
    from src.image.image import add_image_urls
    from src.pricing.pricing import calculate_pricing

    # 이미지 URL 추가
    df_final = add_image_urls(df_final)

    # 구독료 계산
    df_final = calculate_pricing(df_final)

    # 한국어 보조금 컬럼 제거
    df_final = remove_korean_subsidy_columns(df_final)

    # 칼럼 순서 조정 적용
    df_final = reorder_columns(df_final)

    return df_final


def create_all_file(date_str, cleaned_df):
    """전체 결과 파일 생성 (전체 차량)"""
    from src.config.constants import FilePaths

    df_all = process_final_data(cleaned_df)

    all_filename = FilePaths.get_results_file("all", date_str)
    df_all.to_excel(all_filename, index=False)
    print(f"✅ 전체 결과 파일 생성: {all_filename}")
    print(f"📊 전체 차량: {len(df_all)}대, {len(df_all.columns)}개 컬럼")
    return True


def create_upload_file(date_str, listed_df):
    """업로드용 컬럼으로 구성된 파일 생성 (필터링된 데이터)"""
    from src.config.constants import FilePaths

    df_upload = listed_df.copy()

    # 선택된 컬럼만 추출
    selected_columns = [
        "code_sales_a",
        "code_sales_b",
        "code_color_a",
        "code_color_b",
        "request",
        "stock",
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
        "price_total",
        "price_options",
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

    upload_filename = FilePaths.get_results_file("upload", date_str)
    df_upload.to_excel(upload_filename, index=False)
    print(f"✅ 업로드 결과 파일 생성: {upload_filename}")
    print(f"📊 필터링된 차량: {len(df_upload)}대, {len(df_upload.columns)}개 컬럼")
    return True


def create_final_result_file(date_str, cleaned_df, listed_df):
    """날짜가 붙은 최종 결과 파일 생성"""
    print(f"\n📋 4단계: 최종 결과 파일 생성...")

    # 선택된 파일 생성 (재고 조건 이상)
    if create_selected_file(date_str, listed_df):
        # 전체 파일 생성 (전체 차량)
        create_all_file(date_str, cleaned_df)
        # 업로드 파일 생성
        create_upload_file(date_str, listed_df)


if __name__ == "__main__":
    main()

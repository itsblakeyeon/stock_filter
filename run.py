#!/usr/bin/env python3
"""
통합 실행 스크립트
클렌징 → 리스팅 → 내보내기 순서로 실행
"""

import sys
import os
import pandas as pd

# src 폴더를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.cleansing.cleansing_unified import clean_all_data
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

    # 2. 통합 리스팅
    print(f"\n📋 2단계: 통합 리스팅 시작...")
    result_dict = listing_main(cleaned_df)
    print(f"✅ 리스팅 완료")

    # 3. 최종 결과 파일 생성 (날짜 포함)
    create_final_result_file(current_date, result_dict)

    print(f"\n🎉 모든 처리 완료!")
    print(f"📅 처리 날짜: {current_date}")
    print(f"📁 결과 폴더: results/")
    print(f"   - stock_filtered_{current_date}.xlsx")
    print(f"     └─ all 시트: 전체 차량 (필터 없음)")
    print(f"     └─ filtered 시트: 필터링된 차량 (전체 컬럼)")
    print(f"     └─ upload 시트: 업로드용 (선택 컬럼만)")


def create_final_result_file(date_str, result_dict):
    """날짜가 붙은 최종 결과 파일 생성 (3개 시트: all, filtered, upload)"""
    from src.config.constants import FilePaths
    from datetime import datetime

    print(f"\n📋 3단계: 최종 결과 파일 생성...")

    # 3개 시트로 저장
    output_filename = FilePaths.get_results_file("filtered", date_str)

    # ExcelWriter 옵션 설정 (Excel 호환성 향상)
    with pd.ExcelWriter(output_filename, engine='openpyxl', mode='w') as writer:
        # all 시트: 전체 데이터 (필터 없음)
        result_dict["all"].to_excel(writer, sheet_name='all', index=False)
        print(f"   ✅ all 시트 생성: {len(result_dict['all'])}대")

        # filtered 시트: 필터링된 데이터
        result_dict["filtered"].to_excel(writer, sheet_name='filtered', index=False)
        print(f"   ✅ filtered 시트 생성: {len(result_dict['filtered'])}대")

        # upload 시트: 업로드용 데이터 (선택 컬럼만)
        upload_columns = [
            "code_sales_a",
            "code_sales_b",
            "code_color_a",
            "code_color_b",
            "request",
            "stock",
            "company",
            "model",
            "trim",
            "year",
            "fuel",
            "options",
            "wheel_tire",
            "color_exterior",
            "color_interior",
            "price"
        ]

        # 존재하는 컬럼만 선택
        available_columns = [col for col in upload_columns if col in result_dict["filtered"].columns]
        upload_df = result_dict["filtered"][available_columns].copy()
        upload_df.to_excel(writer, sheet_name='upload', index=False)
        print(f"   ✅ upload 시트 생성: {len(upload_df)}대, {len(upload_df.columns)}개 컬럼")

    print(f"✅ 결과 파일 생성 완료: {output_filename}")
    print(f"📊 전체 차량: {len(result_dict['all'])}대, 필터링된 차량: {len(result_dict['filtered'])}대")


if __name__ == "__main__":
    main()

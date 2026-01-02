#!/usr/bin/env python3
import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.cleansing.cleansing_unified import clean_all_data


def main(cleaned_df=None):
    print("🚗 현대차 + 기아차 통합 재고 리스트 생성 시작...")

    # 1. 통합 데이터 전처리 (이미 제공된 경우 사용, 아니면 새로 생성)
    if cleaned_df is None:
        cleaned_df = clean_all_data()

    result_df = cleaned_df

    # 2. 재고 필터링 및 추가 조건 적용
    result_df["stock"] = pd.to_numeric(result_df["stock"], errors="coerce")
    result_df["stock"] = result_df["stock"].fillna(0).astype(int)

    # 전체 데이터 (필터 없음)
    print(f"🔍 필터링 전: {len(result_df)}대, 컬럼 수: {len(result_df.columns)}")
    all_df = result_df.copy()
    print(f"📋 전체 데이터 (필터 없음): {len(all_df)}대")

    # 재고 필터링 (3개 이상)
    filtered_df = result_df[result_df["stock"] >= 3].copy()
    print(f"🔍 재고 3개 이상 필터 후: {len(filtered_df)}대")

    # 추가 필터링 조건 적용
    # 1) 기본 휠&타이어만 (GV70은 18인치가 기본)
    if len(filtered_df) > 0:

        def is_basic_wheel_tire(row):
            wheel_tire = str(row.get("wheel_tire", "")).strip()
            company = str(row.get("company", "")).strip()

            # 제네시스 브랜드는 18인치를 기본으로 간주
            if company == "제네시스" and "18인치" in wheel_tire:
                return True

            # 일반적인 기본 휠&타이어
            return wheel_tire == "기본 휠&타이어"

        filtered_df = filtered_df[filtered_df.apply(is_basic_wheel_tire, axis=1)].copy()
        print(f"🔍 기본 휠&타이어 필터 후 (제네시스 18인치 포함): {len(filtered_df)}대")

    # 2) 빌트인캠만 또는 무옵션 차량 필터링
    def filter_builtin_cam_or_no_option(df):
        def has_builtin_cam_only_or_no_option(option_str):
            if pd.isna(option_str) or option_str == "":
                return True  # 무옵션 포함
            option_str = str(option_str).strip()
            if option_str == "" or option_str == "무옵션":
                return True  # 무옵션 포함
            # 정확히 빌트인캠 또는 빌트인 캠 패키지만 있는지 확인 (외옵션 제외)
            options = [opt.strip() for opt in option_str.split(",") if opt.strip()]
            if len(options) == 1:
                option = options[0]
                # 정확한 빌트인캠 옵션명만 허용 (외옵션 포함된 것은 제외)
                return (
                    option == "빌트인캠"
                    or option == "빌트인 캠 패키지"
                    or option == "빌트인캠2"
                )
            return False

        return df[df["options"].apply(has_builtin_cam_only_or_no_option)]

    filtered_df = filter_builtin_cam_or_no_option(filtered_df)
    print(f"🔍 빌트인캠 또는 무옵션 필터 후: {len(filtered_df)}대")

    # 3) 싼타페 하이브리드 5인승 & 팰리세이드 9인승 필터링
    def filter_seating_requirements(df):
        def should_exclude_by_seating(row):
            model = str(row.get("model", "")).strip()
            trim_raw = str(row.get("trim_raw", "")).strip()

            # 싼타페 하이브리드인 경우: 6인승, 7인승 제외 (5인승만)
            if model == "싼타페 하이브리드":
                if "6인승" in trim_raw or "7인승" in trim_raw:
                    return True  # 제외

            # 팰리세이드인 경우: 7인승, 8인승 제외 (9인승만)
            if "팰리세이드" in model or "디 올 뉴 팰리세이드" in model:
                if "7인승" in trim_raw or "8인승" in trim_raw:
                    return True  # 제외

            return False  # 포함

        return df[~df.apply(should_exclude_by_seating, axis=1)]

    filtered_df = filter_seating_requirements(filtered_df)
    print(
        f"🔍 승차정원 필터 후 (싼타페하이브리드 5인승, 팰리세이드 9인승): {len(filtered_df)}대"
    )

    print(f"\n✅ 완료!")
    print(f"📋 전체 데이터 (all 시트): {len(all_df)}대")
    print(f"📋 필터링된 데이터 (filtered 시트): {len(filtered_df)}대")
    print(
        f"📊 필터링 조건: 재고 3개 이상 + 기본 휠&타이어 + (빌트인캠 또는 무옵션) + 싼타페하이브리드 5인승 + 팰리세이드 9인승"
    )

    # 5. 전체 데이터와 필터링된 데이터 모두 반환
    return {"all": all_df, "filtered": filtered_df}


if __name__ == "__main__":
    main()

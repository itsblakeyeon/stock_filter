#!/usr/bin/env python3
import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.cleansing.cleansing_unified import clean_all_data
from src.pricing.pricing import calculate_pricing
from src.image.image import add_image_urls


def main(cleaned_df=None):
    print("🚗 현대차 + 기아차 통합 재고 리스트 생성 시작...")

    # 1. 통합 데이터 전처리 (이미 제공된 경우 사용, 아니면 새로 생성)
    if cleaned_df is None:
        cleaned_df = clean_all_data()

    # 2. 이미지 URL 추가
    image_df = add_image_urls(cleaned_df)

    # 3. 프라이싱 적용 (이미 완료된 경우 사용)
    if "반납형_12개월" in image_df.columns:
        result_df = image_df
    else:
        from src.pricing.pricing_unified import main as pricing_main

        result_df = pricing_main(image_df)

    # 4. 재고 필터링 및 추가 조건 적용
    result_df["stock"] = pd.to_numeric(result_df["stock"], errors="coerce")
    result_df["stock"] = result_df["stock"].fillna(0).astype(int)

    # 재고 제한 없음
    print(f"🔍 필터링 전: {len(result_df)}대, 컬럼 수: {len(result_df.columns)}")

    filtered_df = result_df.copy()
    print(f"🔍 재고 제한 없음: {len(filtered_df)}대")

    # 추가 필터링 조건 적용
    # 1) 가격 정보 있는 차량만 (price_car_tax_pre, price_car_tax_post, price_options가 ?가 아닌 것)
    def has_valid_price_info(row):
        price_pre = str(row.get("price_car_tax_pre", "?")).strip()
        price_post = str(row.get("price_car_tax_post", "?")).strip()
        price_options = str(row.get("price_options", "?")).strip()

        return (
            price_pre != "?"
            and price_pre != ""
            and pd.notna(row.get("price_car_tax_pre"))
            and price_post != "?"
            and price_post != ""
            and pd.notna(row.get("price_car_tax_post"))
            and price_options != "?"
            and price_options != ""
            and pd.notna(row.get("price_options"))
        )

    # 가격 컬럼 상태 디버깅
    print(f"🔍 가격 컬럼 존재 여부:")
    print(
        f"  - price_car_tax_pre: {'✅' if 'price_car_tax_pre' in filtered_df.columns else '❌'}"
    )
    print(
        f"  - price_car_tax_post: {'✅' if 'price_car_tax_post' in filtered_df.columns else '❌'}"
    )
    print(
        f"  - price_options: {'✅' if 'price_options' in filtered_df.columns else '❌'}"
    )

    if "price_car_tax_pre" in filtered_df.columns:
        unique_pre = filtered_df["price_car_tax_pre"].unique()[:3]
        print(f"  - price_car_tax_pre 샘플: {unique_pre}")

    filtered_df = filtered_df[filtered_df.apply(has_valid_price_info, axis=1)].copy()
    print(f"🔍 가격 정보 필터 후: {len(filtered_df)}대")

    # 2) 기본 휠&타이어만 (GV70은 18인치가 기본)
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

    # 3) 빌트인캠만 또는 무옵션 차량 필터링
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

    # 4) 싼타페 하이브리드 5인승 & 팰리세이드 9인승 필터링
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

    # 5. 24, 48, 72개월 가격 컬럼 제거
    columns_to_remove = [
        "fee_return_24m",
        "fee_return_48m",
        "fee_return_72m",
        "fee_purchase_24m",
        "fee_purchase_48m",
        "fee_purchase_72m",
    ]
    filtered_df = filtered_df.drop(
        columns=[col for col in columns_to_remove if col in filtered_df.columns]
    )

    # 7. 회사별 통계 출력 (안전한 처리)
    print(f"\n📊 회사별 통계:")
    if len(filtered_df) == 0:
        print("  필터링된 차량이 없습니다.")
    elif "company" not in filtered_df.columns:
        print("  company 컬럼이 존재하지 않습니다.")
    else:
        try:
            company_stats = filtered_df["company"].value_counts()
            for company, count in company_stats.items():
                print(f"  {company}: {count}대")
        except Exception as e:
            print(f"  통계 생성 실패: {e}")

    print(f"\n✅ 완료! {len(filtered_df)}대 차량")
    print(
        f"📊 필터링 조건: 재고 제한 없음 + 가격정보 있음 + 기본 휠&타이어 + (빌트인캠 또는 무옵션) + 싼타페하이브리드 5인승 + 팰리세이드 9인승"
    )
    print(f"📊 구독료 컬럼: {len(filtered_df.columns)-18}개")

    # 8. 필터링된 데이터 반환
    return filtered_df


if __name__ == "__main__":
    main()

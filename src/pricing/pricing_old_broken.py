#!/usr/bin/env python3
"""
Stock 프로젝트의 프라이싱 모듈
Pricing 엔진을 사용하여 기존 기능 유지
"""

import pandas as pd
import sys
import os

# 내부 구현으로 대체 (외부 Pricing 모듈 의존성 제거)

# 새로운 내부 모듈들 import
from src.config.pricing_constants import (
    PricingConfig,
    OptionConfig,
    CostStructure,
    YEAR_INFO,
    SUBSCRIPTION_TERMS,
)
from src.pricing.models import (
    CarCostDetail,
    SubscriptionInput,
    PricingResult,
    CalculationSummary,
)
from src.pricing.price_reference import (
    get_all_subsidy_data,
    find_price_by_trim,
    find_price_by_key,
)

# 간단한 내부 구현 함수들
def calculate_pricing_complete(car_price, option_price=0, fuel_type="", 
                             subsidy_national=0, subsidy_lease=0, company=""):
    """완전한 프라이싱 계산 (간단 버전)"""
    # 기본 차량 비용 계산
    tax = car_price * 0.07
    subsidy_total = (subsidy_national + subsidy_lease) * 10000
    if fuel_type == "전기":
        subsidy_total += PricingConfig.ELECTRIC_TAX_SUBSIDY
    
    total_cost = car_price + tax - subsidy_total + PricingConfig.REGISTRATION_FEE
    
    # 구독료 기본 계산 (간단화)
    subscription_fees = {}
    for term in SUBSCRIPTION_TERMS:
        monthly_fee = total_cost / term * 1.1  # 간단한 수수료 적용
        subscription_fees[f"fee_return_options_{term}m"] = monthly_fee
        subscription_fees[f"fee_purchase_options_{term}m"] = monthly_fee * 0.9
    
    return {
        "total_cost": total_cost,
        "subscription_fees": subscription_fees,
        "care_fee": PricingConfig.CARE_FEE_ELECTRIC if fuel_type == "전기" else PricingConfig.CARE_FEE_OTHER
    }

def calculate_car_cost(car_price, fuel_type="", subsidy_trim="", company=""):
    """차량 비용 계산 (간단 버전)"""
    result = calculate_pricing_complete(car_price, 0, fuel_type, 0, 0, company)
    return None, result["total_cost"]

def calculate_subscription_fees(car_price, fuel_type="", subsidy_trim="", company=""):
    """구독료 계산 (간단 버전)"""
    result = calculate_pricing_complete(car_price, 0, fuel_type, 0, 0, company)
    return result["subscription_fees"]

def calculate_option_fees(price_options):
    """옵션 수수료 계산 (간단 버전)"""
    option_fees = {}
    for term in SUBSCRIPTION_TERMS:
        monthly_fee = price_options * OptionConfig.PREMIUM_RATE / term
        option_fees[f"fee_return_options_{term}m"] = monthly_fee
        option_fees[f"fee_purchase_options_{term}m"] = monthly_fee
    return option_fees

# 기존 코드와의 호환성을 위해 data 변수 생성
subsidy_data = get_all_subsidy_data()


def match_subsidy(subsidy_trim):
    """subsidy_트림을 기반으로 보조금 정보를 매칭하는 함수"""
    if not subsidy_trim or subsidy_trim == "":
        return 0, 0

    # subsidy.py의 데이터에서 매칭
    for row in subsidy_data:
        if row[1] == subsidy_trim:  # trim 컬럼 매칭
            return row[2], row[3]  # 국비 보조금, 리스 보조금

    return 0, 0


def add_subsidy_columns_to_df(df):
    """데이터프레임에 보조금 정보 컬럼을 추가하는 함수 (최적화 버전)"""
    print("💰 보조금 정보 매칭 중...")

    # 보조금 데이터를 DataFrame으로 변환
    subsidy_df = pd.DataFrame(subsidy_data, columns=["company", "trim", "national", "lease"])  # type: ignore

    if not subsidy_df.empty:
        # key_subsidy로 매칭
        merged_df = df.merge(
            subsidy_df[["trim", "national", "lease"]],
            left_on="key_subsidy",
            right_on="trim",
            how="left",
        )

        # 매칭된 보조금 정보 복사 (보조금은 차감되므로 음수로 저장)
        df["subsidy_national"] = -(
            merged_df["national"].fillna(0) * 10000
        )  # 음수로 변환
        df["subsidy_lease"] = -(merged_df["lease"].fillna(0) * 10000)  # 음수로 변환

        # 전기차 세금 보조금
        df["subsidy_tax"] = df["fuel"].apply(
            lambda x: -PricingConfig.ELECTRIC_TAX_SUBSIDY if x == "전기" else 0
        )
    else:
        # 기본값 설정
        df["subsidy_national"] = 0
        df["subsidy_lease"] = 0
        df["subsidy_tax"] = df["fuel"].apply(
            lambda x: -PricingConfig.ELECTRIC_TAX_SUBSIDY if x == "전기" else 0
        )

    print(f"✅ 보조금 정보 매칭 완료: {len(df)}개 차량")
    return df


def match_price_info(model, trim, year=None):
    """모델, 트림, 연식을 기반으로 가격 정보를 매칭하는 함수"""
    if not model or not trim or model == "" or trim == "":
        return {"price_car_pre": "?", "price_car_post": "?"}

    try:
        price_info = find_price_by_trim(model, trim, year)
        if price_info:
            return {
                "price_car_pre": price_info.get("price_car_pre", ""),
                "price_car_post": price_info.get("price_car_post", ""),
            }
        else:
            return {"price_car_pre": "?", "price_car_post": "?"}
    except Exception as e:
        return {"price_car_pre": "?", "price_car_post": "?"}


def add_price_columns_to_df(df):
    """데이터프레임에 가격 정보 컬럼을 추가하는 함수 (벡터화된 Key 필드 매칭)"""
    print("💰 가격 정보 매칭 중...")

    # 가격 컬럼 추가
    df["price_car_tax_pre"] = "?"
    df["price_car_tax_post"] = "?"

    # key_admin 필드가 있는지 확인
    if "key_admin" in df.columns:
        # 가격 참조 데이터 로드
        from src.pricing.price_reference import get_price_data

        price_df = get_price_data()

        if not price_df.empty and "key" in price_df.columns:
            # key_admin 필드로 벡터화된 매칭
            merged_df = df.merge(
                price_df[["key", "price_car_pre", "price_car_post"]],
                left_on="key_admin",
                right_on="key",
                how="left",
            )

            # 매칭된 가격 정보 복사
            df["price_car_tax_pre"] = merged_df["price_car_pre"].fillna("?")
            df["price_car_tax_post"] = merged_df["price_car_post"].fillna("?")
        else:
            print("⚠️ 가격 참조 데이터에 Key 필드가 없습니다.")
    else:
        # 기존 방식 (모델, 트림, 연식 개별 매칭)
        for idx, row in df.iterrows():
            model = row.get("model", "")
            trim = row.get("trim", "")
            year = row.get("year", "")

            price_info = match_price_info(model, trim, year)
            if price_info:
                df.at[idx, "price_car_tax_pre"] = price_info["price_car_pre"]
                df.at[idx, "price_car_tax_post"] = price_info["price_car_post"]

    print(f"✅ 가격 정보 매칭 완료: {len(df)}개 차량")
    return df


def calculate_car_cost(car_price, fuel_type="", subsidy_trim="", company=""):
    """
    차량 비용 계산 - Pricing 엔진 사용
    기존 인터페이스 호환성 유지
    """
    # 보조금 계산
    subsidy_national, subsidy_lease = match_subsidy(subsidy_trim)
    
    # Pricing 엔진 사용
    from Pricing import calculate_car_cost as pricing_calculate_car_cost
    car_cost_detail, total_cost = pricing_calculate_car_cost(
        car_price=car_price,
        fuel_type=fuel_type,
        subsidy_national=subsidy_national,
        subsidy_lease=subsidy_lease,
        company=company
    )
    
    # 기존 형식으로 변환
    car = {
        "car": car_cost_detail.car,
        "tax": car_cost_detail.tax,
        "subsidy_national": car_cost_detail.subsidy_national,
        "subsidy_lease": car_cost_detail.subsidy_lease,
        "subsidy_tax": car_cost_detail.subsidy_tax,
        "rebate": car_cost_detail.rebate,
        "plate": car_cost_detail.plate,
        "promo": car_cost_detail.promo,
    }
    return car, total_cost


def get_cost_structure():
    """비용 구조 반환 - Pricing 엔진 사용"""
    from Pricing.core.calculations import get_cost_structure as pricing_get_cost_structure
    return pricing_get_cost_structure()


def calculate_residual_values(car_cost):
    """잔존가치 계산 - Pricing 엔진 사용"""
    from Pricing.core.calculations import calculate_residual_values as pricing_calculate_residual_values
    return pricing_calculate_residual_values(car_cost)


def calculate_subscription_fees(car_price, fuel_type="", subsidy_trim="", company=""):
    """구독료 계산 메인 함수 - Pricing 엔진 사용"""
    # 보조금 정보 가져오기
    subsidy_national, subsidy_lease = match_subsidy(subsidy_trim)
    
    # Pricing 엔진 사용
    subscription_input = SubscriptionInput(
        car_price=car_price,
        fuel_type=fuel_type,
        subsidy_national=subsidy_national,
        subsidy_lease=subsidy_lease,
        company=company,
        terms=[12, 36, 60, 84]
    )
    
    from Pricing.core.calculations import calculate_subscription_fees as pricing_calculate_subscription_fees
    return pricing_calculate_subscription_fees(subscription_input)


def calculate_option_fees(price_options):
    """옵션 프라이싱 계산 함수 - Pricing 엔진 사용"""
    from Pricing.core.calculations import calculate_option_fees as pricing_calculate_option_fees
    return pricing_calculate_option_fees(price_options, [12, 36, 60, 84])


def calculate_pricing(df):
    """전처리된 데이터에 모든 가격 관련 계산을 적용하는 함수"""
    print("💰 가격 계산 시작...")

    # 1. 보조금 정보 매칭
    df = add_subsidy_columns_to_df(df)

    # 2. 가격 정보 매칭
    df = add_price_columns_to_df(df)

    # 3. 차량 비용 계산
    # price_car_tax_post가 "?"인 경우 price_car_original 사용
    df["price_tax"] = df.apply(
        lambda row: (
            float(row["price_car_tax_post"])
            if pd.notna(row["price_car_tax_post"]) and row["price_car_tax_post"] != "?"
            else float(row["price_car_original"])
        )
        * 0.07,
        axis=1,
    )
    df["price_registration"] = PricingConfig.REGISTRATION_FEE
    df["rebate"] = df.apply(
        lambda row: -(
            float(row["price_car_tax_post"])
            if pd.notna(row["price_car_tax_post"]) and row["price_car_tax_post"] != "?"
            else float(row["price_car_original"])
        )
        * 0.01 if str(row.get("company", "")).strip() != "테슬라" else 0,
        axis=1,
    )
    df["promotion"] = 0
    df["price_total"] = df.apply(
        lambda row: (
            float(row["price_car_tax_post"])
            if pd.notna(row["price_car_tax_post"]) and row["price_car_tax_post"] != "?"
            else float(row["price_car_original"])
        )
        + row["price_tax"]
        + row["subsidy_national"]
        + row["subsidy_lease"]
        + row["subsidy_tax"]
        + row["rebate"]
        + PricingConfig.REGISTRATION_FEE,
        axis=1,
    )

    # 3-1. 옵션 가격 계산 (price_car_original - price_car_tax_pre)
    print("💰 옵션 가격 계산 중...")
    df["price_options"] = "?"
    for idx, row in df.iterrows():
        try:
            # price_car_tax_pre가 "?"면 계산 불가
            if pd.isna(row["price_car_tax_pre"]) or row["price_car_tax_pre"] == "?":
                df.at[idx, "price_options"] = "?"
                continue

            price_car_original = (
                float(row["price_car_original"])
                if pd.notna(row["price_car_original"])
                and row["price_car_original"] != "?"
                else 0
            )
            price_car_tax_pre = float(row["price_car_tax_pre"])
            df.at[idx, "price_options"] = max(0, price_car_original - price_car_tax_pre)
        except (ValueError, TypeError):
            df.at[idx, "price_options"] = "?"
    print(f"✅ 옵션 가격 계산 완료: {len(df)}개 차량")

    # 4. 구독료 계산
    print("구독료 계산 시작...")
    subscription_columns = []
    for idx, row in df.iterrows():
        if idx % 50 == 0:
            print(f"  {idx+1}/{len(df)} 차량 처리 중...")

        car_price = (
            float(row["price_car_tax_post"])
            if pd.notna(row["price_car_tax_post"]) and row["price_car_tax_post"] != "?"
            else float(row["price_car_original"])
        )
        if pd.isna(car_price) or car_price <= 0:
            car_price = PricingConfig.DEFAULT_CAR_PRICE

        # 보조금 정보 가져오기
        fuel_type = str(row["fuel"]) if pd.notna(row["fuel"]) else ""
        subsidy_trim = str(row["key_subsidy"]) if pd.notna(row["key_subsidy"]) else ""
        company = str(row["company"]) if pd.notna(row["company"]) else ""

        fees = calculate_subscription_fees(car_price, fuel_type, subsidy_trim, company)

        for fee_name, fee_value in fees.items():
            if fee_name not in subscription_columns:
                subscription_columns.append(fee_name)
                df[fee_name] = 0
            df.at[idx, fee_name] = fee_value

    # 4-1. 옵션 프라이싱 계산
    print("옵션 프라이싱 계산 시작...")
    option_columns = []
    for idx, row in df.iterrows():
        if idx % 50 == 0:
            print(f"  {idx+1}/{len(df)} 차량 옵션 처리 중...")

        # price_options이 유효한 값인지 확인
        price_options = row.get("price_options", 0)
        if pd.isna(price_options) or price_options == "?" or price_options == 0:
            # 옵션 요금을 0으로 설정 (12, 36, 60, 84개월만)
            for term in [12, 36, 60, 84]:
                fee_name = f"fee_options_{term}m"
                if fee_name not in option_columns:
                    option_columns.append(fee_name)
                    df[fee_name] = 0
                df.at[idx, fee_name] = 0
        else:
            try:
                price_options = float(price_options)
                option_fees = calculate_option_fees(price_options)

                for fee_name, fee_value in option_fees.items():
                    if fee_name not in option_columns:
                        option_columns.append(fee_name)
                        df[fee_name] = 0
                    df.at[idx, fee_name] = fee_value
            except (ValueError, TypeError):
                # 옵션 요금을 0으로 설정
                for term in [12, 36, 60, 84]:
                    fee_name = f"fee_options_{term}m"
                    if fee_name not in option_columns:
                        option_columns.append(fee_name)
                        df[fee_name] = 0
                    df.at[idx, fee_name] = 0

    # 5. 옵션이 포함된 구독료 필드 생성 (12, 36, 60, 84개월만)
    print("💰 옵션 포함 구독료 계산 중...")
    terms = [12, 36, 60, 84]

    for term in terms:
        # 반납형 + 옵션
        return_col = f"fee_return_{term}m"
        options_col = f"fee_options_{term}m"
        return_options_col = f"fee_return_options_{term}m"

        if return_col in df.columns and options_col in df.columns:
            df[return_options_col] = df[return_col] + df[options_col]

        # 인수형 + 옵션
        purchase_col = f"fee_purchase_{term}m"
        purchase_options_col = f"fee_purchase_options_{term}m"

        if purchase_col in df.columns and options_col in df.columns:
            df[purchase_options_col] = df[purchase_col] + df[options_col]

    print(f"✅ 구독료 계산 완료! {len(subscription_columns)}개 구독료 컬럼")

    # 6. 추가 필드 생성 (옵션 포함 구독료 계산 후)
    df["fee_care"] = df["fuel"].apply(
        lambda x: (
            PricingConfig.CARE_FEE_ELECTRIC
            if x == "전기"
            else PricingConfig.CARE_FEE_OTHER
        )
    )
    df["fee_list"] = df["fee_return_options_12m"]

    print("✅ 가격 계산 완료!")
    return df
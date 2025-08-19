#!/usr/bin/env python3
"""
Stock 프로젝트의 프라이싱 모듈 (새 버전)
외부 Pricing 의존성 제거하고 내부 구현으로 대체
"""

import pandas as pd
import sys
import os

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


def calculate_pricing_complete(car_price, option_price=0, fuel_type="", 
                             subsidy_national=0, subsidy_lease=0, company=""):
    """완전한 프라이싱 계산"""
    # 기본 차량 비용 계산
    tax = car_price * 0.07
    subsidy_total = (subsidy_national + subsidy_lease) * 10000
    if fuel_type == "전기":
        subsidy_total += PricingConfig.ELECTRIC_TAX_SUBSIDY
    
    total_cost = car_price + tax - subsidy_total + PricingConfig.REGISTRATION_FEE
    
    # 구독료 기본 계산
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
    """차량 비용 계산"""
    result = calculate_pricing_complete(car_price, 0, fuel_type, 0, 0, company)
    return None, result["total_cost"]


def calculate_subscription_fees(car_price, fuel_type="", subsidy_trim="", company=""):
    """구독료 계산"""
    result = calculate_pricing_complete(car_price, 0, fuel_type, 0, 0, company)
    return result["subscription_fees"]


def calculate_option_fees(price_options):
    """옵션 수수료 계산"""
    option_fees = {}
    for term in SUBSCRIPTION_TERMS:
        monthly_fee = price_options * OptionConfig.PREMIUM_RATE / term
        option_fees[f"fee_return_options_{term}m"] = monthly_fee
        option_fees[f"fee_purchase_options_{term}m"] = monthly_fee
    return option_fees


def get_cost_structure(car_price):
    """비용 구조를 가져오는 함수"""
    return {
        "initial": CostStructure.INITIAL_COSTS,
        "recurring": CostStructure.RECURRING_YEARLY_COSTS
    }


def calculate_residual_values(car_price, company=""):
    """잔가 계산"""
    residuals = {}
    for year_key, year_data in YEAR_INFO.items():
        residuals[year_key] = car_price * year_data["discount"]
    return residuals


def match_price_info(trim):
    """가격 정보 매칭"""
    return find_price_by_trim(trim)


def add_price_columns_to_df(df):
    """DataFrame에 가격 컬럼 추가"""
    if "price_total" not in df.columns:
        df["price_total"] = PricingConfig.DEFAULT_CAR_PRICE
    if "price_options" not in df.columns:
        df["price_options"] = 0
    return df


def add_subsidy_columns_to_df(df):
    """DataFrame에 보조금 컬럼 추가"""
    if "subsidy_national" not in df.columns:
        df["subsidy_national"] = 0
    if "subsidy_lease" not in df.columns:
        df["subsidy_lease"] = 0
    return df


def calculate_pricing(df):
    """DataFrame에 구독료 계산 결과 추가"""
    # 기본 컬럼 추가
    df["price_registration"] = PricingConfig.REGISTRATION_FEE
    
    for index, row in df.iterrows():
        car_price = row.get("price_total", PricingConfig.DEFAULT_CAR_PRICE)
        price_options = row.get("price_options", 0)
        fuel_type = row.get("fuel", "")
        subsidy_trim = row.get("subsidy_trim", "")
        company = row.get("company", "")

        try:
            # 구독료 계산
            fees = calculate_subscription_fees(car_price, fuel_type, subsidy_trim, company)
            
            # 구독료 컬럼 추가
            for term in SUBSCRIPTION_TERMS:
                return_key = f"fee_return_options_{term}m"
                purchase_key = f"fee_purchase_options_{term}m"
                df.at[index, return_key] = fees.get(return_key, 0)
                df.at[index, purchase_key] = fees.get(purchase_key, 0)

            # 옵션 수수료 계산 및 추가
            if price_options > 0:
                option_fees = calculate_option_fees(price_options)
                for term in SUBSCRIPTION_TERMS:
                    return_key = f"fee_return_options_{term}m"
                    purchase_key = f"fee_purchase_options_{term}m"
                    df.at[index, return_key] += option_fees.get(return_key, 0)
                    df.at[index, purchase_key] += option_fees.get(purchase_key, 0)

        except Exception as e:
            print(f"Error processing row {index}: {e}")
            # 기본값 설정
            for term in SUBSCRIPTION_TERMS:
                df.at[index, f"fee_return_options_{term}m"] = 0
                df.at[index, f"fee_purchase_options_{term}m"] = 0

    # 케어 비용 추가
    df["fee_care"] = df["fuel"].apply(
        lambda x: PricingConfig.CARE_FEE_ELECTRIC
        if x == "전기"
        else PricingConfig.CARE_FEE_OTHER
    )

    # 리스트 비용 (임시로 1000000 설정)
    df["fee_list"] = 1000000

    return df
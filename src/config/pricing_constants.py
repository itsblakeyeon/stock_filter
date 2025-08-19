#!/usr/bin/env python3
"""
프라이싱 관련 상수들
모든 프라이싱 계산에서 사용되는 상수값들을 중앙 관리
"""


class PricingConfig:
    """프라이싱 관련 상수"""
    # 금융 파라미터
    INTEREST_RATE = 0.11
    DEPRECIATION_RATE_5_YEARS = 0.13
    DEPRECIATION_RATE_6_YEARS = 0.12
    DOWN_PAYMENT_RATE = 0.20
    
    # 대손 계수
    RETURN_TYPE_LOSS = 1.02
    PURCHASE_TYPE_LOSS = 1.02
    
    # 기본값
    DEFAULT_CAR_PRICE = 39510000.0
    REGISTRATION_FEE = 200000
    
    # 케어 비용
    CARE_FEE_ELECTRIC = 40000
    CARE_FEE_OTHER = 0
    
    # 전기차 세금 보조금
    ELECTRIC_TAX_SUBSIDY = 1400000


class OptionConfig:
    """옵션 프라이싱 설정"""
    PREMIUM_RATE = 0.50  # 50%


class CostStructure:
    """비용 구조 상수"""
    # 초기 비용
    INITIAL_COSTS = {
        "adv": 1500000,
        "blackbox": 50000,
        "tint_highpass": 60000,
        "delivery": 200000,
        "misc": 10000,
    }
    
    # 연간 반복 비용
    RECURRING_YEARLY_COSTS = {
        "labor": 600000,
        "car_tax": 720000,
        "monitoring": 132000,
    }


# 연도별 정보
YEAR_INFO = {
    "Y0": {"term": 0, "discount": 1.00, "troi": {"반납형": None, "인수형": None}},
    "Y1": {"term": 12, "discount": 0.94, "troi": {"반납형": 6, "인수형": 12}},
    "Y2": {"term": 24, "discount": 0.89, "troi": {"반납형": 6, "인수형": 12}},
    "Y3": {"term": 36, "discount": 0.84, "troi": {"반납형": 6, "인수형": 12}},
    "Y4": {"term": 48, "discount": 0.79, "troi": {"반납형": 6, "인수형": 12}},
    "Y5": {"term": 60, "discount": 0.75, "troi": {"반납형": 6, "인수형": 12}},
    "Y6": {"term": 72, "discount": 0.71, "troi": {"반납형": 6, "인수형": 12}},
    "Y7": {"term": 84, "discount": 0.67, "troi": {"반납형": 6, "인수형": 12}},
}


# 구독료 계산에 사용되는 기간들
SUBSCRIPTION_TERMS = [12, 36, 60, 84]
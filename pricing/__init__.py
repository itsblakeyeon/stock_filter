#!/usr/bin/env python3
"""
Pricing 모듈
차량 프라이싱 계산 엔진

사용법:
    from Pricing import calculate_pricing_complete, SubscriptionInput
    
    result = calculate_pricing_complete(
        car_price=50000000,
        option_price=2000000,
        fuel_type="전기",
        subsidy_national=80,
        subsidy_lease=0,
        company="현대"
    )
"""

from .core import (
    # 주요 함수들
    calculate_pricing_complete,
    calculate_subscription_fees,
    calculate_car_cost,
    calculate_option_fees,
    
    # 데이터 모델
    SubscriptionInput,
    PricingResult,
    CarCostDetail,
    
    # 상수들
    PricingConfig,
    OptionConfig,
    CostStructure,
    SUBSCRIPTION_TERMS,
    
    # 가격 참조
    load_price_reference_data,
    get_subsidy_data,
    get_price_data,
    get_subsidy_info,
    get_price_info
)

__version__ = "1.0.0"

__all__ = [
    'calculate_pricing_complete',
    'calculate_subscription_fees', 
    'calculate_car_cost',
    'calculate_option_fees',
    'SubscriptionInput',
    'PricingResult',
    'CarCostDetail',
    'PricingConfig',
    'OptionConfig',
    'CostStructure',
    'SUBSCRIPTION_TERMS',
    'load_price_reference_data',
    'get_subsidy_data',
    'get_price_data',
    'get_subsidy_info',
    'get_price_info'
]
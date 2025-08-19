#!/usr/bin/env python3
"""
프라이싱 관련 데이터 모델
계산 결과와 입력 데이터의 구조를 정의
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class CarCostDetail:
    """차량 비용 상세"""
    car: float                    # 차량 가격
    tax: float                    # 세금 (7%)
    subsidy_national: float       # 국비 보조금 (차감, 음수)
    subsidy_lease: float          # 리스 보조금 (차감, 음수)
    subsidy_tax: float           # 전기차 세금 보조금 (차감, 음수)
    rebate: float                # 리베이트 (차감, 음수)
    plate: float                 # 등록비
    promo: float                 # 프로모션


@dataclass
class SubscriptionInput:
    """구독료 계산 입력 데이터"""
    car_price: float
    fuel_type: str = ""
    subsidy_national: float = 0   # 만원 단위
    subsidy_lease: float = 0      # 만원 단위
    company: str = ""
    terms: list = None
    
    def __post_init__(self):
        if self.terms is None:
            self.terms = [12, 36, 60, 84]


@dataclass
class PricingResult:
    """완전한 프라이싱 계산 결과"""
    car_cost_detail: CarCostDetail
    total_car_cost: float
    subscription_fees: Dict[str, float]
    option_fees: Dict[str, float]
    combined_fees: Dict[str, float]
    care_fee: float
    summary: Dict[str, float]


@dataclass
class CalculationSummary:
    """계산 요약 정보"""
    차량가격: float
    옵션가격: float
    총차량비용: float
    케어비용: float
    세금: float
    보조금합계: float
    리베이트: float
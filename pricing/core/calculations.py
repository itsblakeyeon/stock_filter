#!/usr/bin/env python3
"""
핵심 프라이싱 계산 로직
모든 계산 함수들이 여기에 정의됨
"""

import math
from typing import Dict, List, Tuple

from .constants import PricingConfig, CostStructure, YEAR_INFO, OptionConfig
from .models import CarCostDetail, SubscriptionInput, PricingResult, CalculationSummary


def calculate_pmt(principal: float, annual_rate: float, months: int) -> float:
    """월 할부금 계산"""
    r = annual_rate / 12
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def calculate_car_cost(
    car_price: float,
    fuel_type: str = "",
    subsidy_national: float = 0,
    subsidy_lease: float = 0,
    company: str = ""
) -> Tuple[CarCostDetail, float]:
    """
    차량 비용 계산
    
    Args:
        car_price: 차량 가격
        fuel_type: 연료 타입 ("전기" 등)
        subsidy_national: 국비 보조금 (만원 단위)
        subsidy_lease: 리스 보조금 (만원 단위)
        company: 제조사 ("테슬라" 제외시 리베이트 적용)
    
    Returns:
        CarCostDetail: 비용 상세
        float: 총 비용
    """
    # 세금 계산 (7%)
    tax = car_price * 0.07
    
    # 보조금 계산 (차감되므로 음수)
    subsidy_national_amount = -(subsidy_national * 10000)
    subsidy_lease_amount = -(subsidy_lease * 10000)
    subsidy_tax = -PricingConfig.ELECTRIC_TAX_SUBSIDY if fuel_type == "전기" else 0
    
    # 리베이트 계산 (테슬라 제외)
    rebate = -(car_price * 0.01) if str(company).strip() != "테슬라" else 0

    car_cost_detail = CarCostDetail(
        car=car_price,
        tax=tax,
        subsidy_national=subsidy_national_amount,
        subsidy_lease=subsidy_lease_amount,
        subsidy_tax=subsidy_tax,
        rebate=rebate,
        plate=PricingConfig.REGISTRATION_FEE,
        promo=0
    )
    
    total_cost = (
        car_cost_detail.car + 
        car_cost_detail.tax + 
        car_cost_detail.subsidy_national + 
        car_cost_detail.subsidy_lease + 
        car_cost_detail.subsidy_tax + 
        car_cost_detail.rebate + 
        car_cost_detail.plate + 
        car_cost_detail.promo
    )
    
    return car_cost_detail, total_cost


def get_cost_structure() -> Tuple[float, float]:
    """비용 구조 반환"""
    initial_cost = sum(CostStructure.INITIAL_COSTS.values())
    recurring_cost = sum(CostStructure.RECURRING_YEARLY_COSTS.values())
    return initial_cost, recurring_cost


def calculate_residual_values(car_cost: float) -> Dict[str, float]:
    """잔존가치 계산"""
    ratios = {
        "Y1": 1 - PricingConfig.DEPRECIATION_RATE_5_YEARS,
        "Y2": 1 - PricingConfig.DEPRECIATION_RATE_5_YEARS * 2,
        "Y3": 1 - PricingConfig.DEPRECIATION_RATE_5_YEARS * 3,
        "Y4": 1 - PricingConfig.DEPRECIATION_RATE_5_YEARS * 4,
        "Y5": 1 - PricingConfig.DEPRECIATION_RATE_5_YEARS * 5,
        "Y6": 1 - PricingConfig.DEPRECIATION_RATE_6_YEARS * 6,
        "Y7": 1 - PricingConfig.DEPRECIATION_RATE_6_YEARS * 7,
    }
    return {year: round(car_cost * ratio) for year, ratio in ratios.items()}


def calculate_subscription_return_fee(
    year_label: str, 
    discounted_costs: Dict[str, float], 
    residual_values: Dict[str, float]
) -> float:
    """반납형 구독료 계산"""
    troi = YEAR_INFO[year_label]["troi"]["반납형"]
    year_index = int(year_label[1])

    if year_index <= 5:
        cost_sum = sum(discounted_costs[f"Y{i}"] for i in range(0, 6))
    else:
        cost_sum = sum(discounted_costs[f"Y{i}"] for i in range(0, year_index + 1))

    residual_value = residual_values[year_label]
    discount_factor = YEAR_INFO[year_label]["discount"]
    numerator = ((100 + troi) / 100) * cost_sum - residual_value * discount_factor
    denominator = (
        sum(YEAR_INFO[f"Y{i}"]["discount"] for i in range(1, year_index + 1)) * 12
    )

    subscription_fee = (
        (numerator / denominator) * PricingConfig.RETURN_TYPE_LOSS / 10000
    )
    return math.ceil(subscription_fee) * 10000


def calculate_early_repayment_fees_by_term(
    car_cost: float, 
    down_payment: float, 
    annual_rate: float, 
    total_months: int
) -> Dict[int, Dict[str, float]]:
    """중도상환 수수료 계산"""
    early_fees = {}
    for months in range(12, 85, 12):
        r = annual_rate / 12
        total_principal = car_cost - down_payment
        pmt = calculate_pmt(total_principal, annual_rate, total_months)

        balance = total_principal
        for m in range(1, months + 1):
            interest = balance * r
            principal_payment = pmt - interest
            balance -= principal_payment

        remaining_balance = balance
        early_fee = round(remaining_balance * 0.01)
        early_fees[months] = {"잔금": remaining_balance, "중도상환수수료": early_fee}
    return early_fees


def cost_own_by_year(
    n_years: int,
    down_payment: float,
    init_setup_cost: float,
    installment_payment_yearly: float,
    recurring_cost_1y: float,
    early_repayment_fees_by_term: Dict[int, Dict[str, float]],
) -> float:
    """인수형 연도별 비용 계산"""
    total = (down_payment + init_setup_cost) * YEAR_INFO["Y0"]["discount"]

    for i in range(1, min(n_years, 5) + 1):
        discount = YEAR_INFO.get(f"Y{i}", {"discount": 1.0})["discount"]
        if i == n_years and n_years <= 5:
            term = i * 12
            add = (
                installment_payment_yearly
                + recurring_cost_1y
                + early_repayment_fees_by_term[term]["잔금"]
                + early_repayment_fees_by_term[term]["중도상환수수료"]
            )
        else:
            add = installment_payment_yearly + recurring_cost_1y
        total += add * discount

    if n_years > 5:
        for i in range(6, n_years + 1):
            discount = YEAR_INFO.get(f"Y{i}", {"discount": 1.0})["discount"]
            total += recurring_cost_1y * discount

    return total


def calculate_subscription_own_fee(
    year_label: str,
    down_payment: float,
    init_setup_cost: float,
    installment_payment_yearly: float,
    recurring_cost_1y: float,
    early_repayment_fees_by_term: Dict[int, Dict[str, float]],
) -> float:
    """인수형 구독료 계산"""
    troi = YEAR_INFO[year_label]["troi"]["인수형"]
    year_index = int(year_label[1])

    cost_sum = cost_own_by_year(
        year_index,
        down_payment,
        init_setup_cost,
        installment_payment_yearly,
        recurring_cost_1y,
        early_repayment_fees_by_term,
    )
    numerator = ((100 + troi) / 100) * cost_sum
    denominator = (
        sum(YEAR_INFO[f"Y{i}"]["discount"] for i in range(1, year_index + 1)) * 12
    )

    subscription_fee = (
        (numerator / denominator) * PricingConfig.PURCHASE_TYPE_LOSS / 10000
    )
    return math.ceil(subscription_fee) * 10000


def calculate_option_fees(price_options: float, terms: List[int] = None) -> Dict[str, float]:
    """
    옵션 프라이싱 계산
    
    Args:
        price_options: 옵션 가격
        terms: 계산할 기간 리스트 (개월)
    
    Returns:
        dict: 기간별 옵션 요금
    """
    if terms is None:
        terms = [12, 36, 60, 84]
        
    option_fees = {}
    
    for term in terms:
        # term에 해당하는 year 찾기
        year_count = term // 12
        if term % 12 != 0:
            year_count += 1
        year_count = min(year_count, 7)
        
        discount_sum = sum(
            YEAR_INFO[f"Y{j}"]["discount"] for j in range(1, year_count + 1)
        )
        
        fee = price_options * (1 + OptionConfig.PREMIUM_RATE) / discount_sum / 12
        # 1000원 단위로 라운드업
        option_fees[f"fee_options_{term}m"] = math.ceil(fee / 1000) * 1000

    return option_fees


def calculate_subscription_fees(subscription_input: SubscriptionInput) -> Dict[str, float]:
    """
    구독료 계산 메인 함수
    
    Args:
        subscription_input: 구독료 계산 입력 데이터
    
    Returns:
        dict: 기간별 반납형/인수형 구독료
    """
    # 차량 비용 계산
    car_cost_detail, car_cost = calculate_car_cost(
        subscription_input.car_price, 
        subscription_input.fuel_type, 
        subscription_input.subsidy_national, 
        subscription_input.subsidy_lease, 
        subscription_input.company
    )
    down_payment = car_cost_detail.car * PricingConfig.DOWN_PAYMENT_RATE

    # 할부금 계산
    installment_months = 60
    monthly_payment = calculate_pmt(
        car_cost - down_payment, PricingConfig.INTEREST_RATE, installment_months
    )
    installment_payment_yearly = monthly_payment * 12

    # 비용 구조
    init_setup_cost, recurring_cost_1y = get_cost_structure()

    # 연도별 비용
    cost_by_year = {
        "Y0": down_payment + init_setup_cost,
        "Y1": installment_payment_yearly + recurring_cost_1y,
        "Y2": installment_payment_yearly + recurring_cost_1y,
        "Y3": installment_payment_yearly + recurring_cost_1y,
        "Y4": installment_payment_yearly + recurring_cost_1y,
        "Y5": installment_payment_yearly + recurring_cost_1y,
        "Y6": recurring_cost_1y,
        "Y7": recurring_cost_1y,
    }

    # 할인된 비용
    discounted_costs = {
        year: cost_by_year[year] * YEAR_INFO[year]["discount"] for year in cost_by_year
    }

    # 잔존가치
    residual_values = calculate_residual_values(car_cost)

    # 반납형 구독료
    return_fees = {}
    for term in subscription_input.terms:
        year_count = term // 12
        if term % 12 != 0:
            year_count += 1
        year_count = min(year_count, 7)
        
        year_label = f"Y{year_count}"
        fee = calculate_subscription_return_fee(
            year_label, discounted_costs, residual_values
        )
        return_fees[f"fee_return_{term}m"] = fee

    # 인수형 중도상환 수수료
    early_repayment_fees = calculate_early_repayment_fees_by_term(
        car_cost, down_payment, PricingConfig.INTEREST_RATE, installment_months
    )

    # 인수형 구독료
    own_fees = {}
    for term in subscription_input.terms:
        year_count = term // 12
        if term % 12 != 0:
            year_count += 1
        year_count = min(year_count, 7)
        
        year_label = f"Y{year_count}"
        fee = calculate_subscription_own_fee(
            year_label,
            down_payment,
            init_setup_cost,
            installment_payment_yearly,
            recurring_cost_1y,
            early_repayment_fees,
        )
        own_fees[f"fee_purchase_{term}m"] = fee

    return {**return_fees, **own_fees}


def calculate_pricing_complete(
    car_price: float,
    option_price: float = 0,
    fuel_type: str = "",
    subsidy_national: float = 0,
    subsidy_lease: float = 0,
    company: str = "",
    terms: List[int] = None
) -> PricingResult:
    """
    완전한 프라이싱 계산 (차량 + 옵션)
    
    Args:
        car_price: 차량 가격
        option_price: 옵션 가격
        fuel_type: 연료 타입
        subsidy_national: 국비 보조금 (만원)
        subsidy_lease: 리스 보조금 (만원)
        company: 제조사
        terms: 계산할 기간 리스트
    
    Returns:
        PricingResult: 모든 프라이싱 정보
    """
    if terms is None:
        terms = [12, 36, 60, 84]
        
    # 차량 기본 비용 계산
    car_cost_detail, total_car_cost = calculate_car_cost(
        car_price, fuel_type, subsidy_national, subsidy_lease, company
    )
    
    # 구독료 계산
    subscription_input = SubscriptionInput(
        car_price=car_price,
        fuel_type=fuel_type,
        subsidy_national=subsidy_national,
        subsidy_lease=subsidy_lease,
        company=company,
        terms=terms
    )
    subscription_fees = calculate_subscription_fees(subscription_input)
    
    # 옵션 프라이싱 계산
    option_fees = calculate_option_fees(option_price, terms) if option_price > 0 else {}
    
    # 옵션 포함 구독료 계산
    combined_fees = {}
    for term in terms:
        return_key = f"fee_return_{term}m"
        purchase_key = f"fee_purchase_{term}m"
        option_key = f"fee_options_{term}m"
        
        if return_key in subscription_fees:
            option_amount = option_fees.get(option_key, 0)
            combined_fees[f"fee_return_options_{term}m"] = subscription_fees[return_key] + option_amount
            
        if purchase_key in subscription_fees:
            option_amount = option_fees.get(option_key, 0)
            combined_fees[f"fee_purchase_options_{term}m"] = subscription_fees[purchase_key] + option_amount
    
    # 케어 비용 계산
    care_fee = PricingConfig.CARE_FEE_ELECTRIC if fuel_type == "전기" else PricingConfig.CARE_FEE_OTHER
    
    # 요약 정보
    total_subsidy = (
        car_cost_detail.subsidy_national + 
        car_cost_detail.subsidy_lease + 
        car_cost_detail.subsidy_tax
    )
    
    summary = {
        "차량가격": car_price,
        "옵션가격": option_price,
        "총차량비용": total_car_cost,
        "케어비용": care_fee,
        "세금": car_cost_detail.tax,
        "보조금합계": total_subsidy,
        "리베이트": car_cost_detail.rebate,
    }
    
    return PricingResult(
        car_cost_detail=car_cost_detail,
        total_car_cost=total_car_cost,
        subscription_fees=subscription_fees,
        option_fees=option_fees,
        combined_fees=combined_fees,
        care_fee=care_fee,
        summary=summary
    )
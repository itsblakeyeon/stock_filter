#!/usr/bin/env python3
"""
Pricing 모듈 사용 예시
다양한 사용 방법과 시나리오 예시
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calculator import calculate_pricing, print_pricing_result, quick_calculate
from core import calculate_pricing_complete


def example_basic_usage():
    """기본 사용법 예시"""
    print("🚗 기본 사용법 예시")
    print("="*50)
    
    # 간단한 계산
    result = quick_calculate(
        car_price=50000000,    # 5천만원
        fuel_type="전기",
        subsidy_national=80,   # 800만원 보조금
        company="현대"
    )
    
    print("빠른 계산 결과:")
    for key, value in result.items():
        print(f"  {key}: {value:,}원")


def example_detailed_calculation():
    """상세 계산 예시"""
    print("\n🔍 상세 계산 예시")
    print("="*50)
    
    # 상세한 계산
    result = calculate_pricing(
        car_price=55000000,      # 차량 가격
        option_price=3000000,    # 옵션 가격
        fuel_type="전기",        # 연료 타입
        subsidy_national=80,     # 국비 보조금 (만원)
        subsidy_lease=20,        # 리스 보조금 (만원)
        company="현대",          # 제조사
        terms=[12, 24, 36, 60, 84]  # 계산할 기간
    )
    
    print_pricing_result(result)


def example_multiple_scenarios():
    """여러 시나리오 비교 예시"""
    print("\n📊 시나리오 비교 예시")
    print("="*50)
    
    scenarios = [
        {
            "name": "아이오닉 6 (전기차)",
            "car_price": 52000000,
            "option_price": 2500000,
            "fuel_type": "전기",
            "subsidy_national": 80,
            "company": "현대"
        },
        {
            "name": "그랜저 (가솔린)",
            "car_price": 45000000,
            "option_price": 1500000,
            "fuel_type": "가솔린",
            "subsidy_national": 0,
            "company": "현대"
        },
        {
            "name": "테슬라 Model 3",
            "car_price": 60000000,
            "option_price": 0,
            "fuel_type": "전기",
            "subsidy_national": 0,  # 테슬라는 보조금 적용 안됨
            "company": "테슬라"
        }
    ]
    
    results = []
    for scenario in scenarios:
        result = quick_calculate(
            car_price=scenario["car_price"],
            fuel_type=scenario["fuel_type"],
            subsidy_national=scenario["subsidy_national"],
            company=scenario["company"]
        )
        results.append({
            "name": scenario["name"],
            "total_cost": result["총차량비용"],
            "return_12m": result["12개월_반납형"],
            "return_36m": result["36개월_반납형"],
            "purchase_36m": result["36개월_인수형"]
        })
    
    # 비교 표 출력
    print(f"{'차량명':<15} {'총비용':<12} {'반납12개월':<12} {'반납36개월':<12} {'인수36개월':<12}")
    print("-" * 65)
    for r in results:
        print(f"{r['name']:<15} {r['total_cost']:>10,}원 {r['return_12m']:>10,}원 {r['return_36m']:>10,}원 {r['purchase_36m']:>10,}원")


def example_option_impact():
    """옵션 가격 영향 분석 예시"""
    print("\n⚙️ 옵션 가격 영향 분석")
    print("="*50)
    
    base_car_price = 50000000
    option_prices = [0, 1000000, 2000000, 3000000, 5000000]
    
    print(f"차량 기본가: {base_car_price:,}원")
    print(f"{'옵션가격':<12} {'36개월 반납형':<15} {'옵션 포함':<15} {'차이':<10}")
    print("-" * 55)
    
    for option_price in option_prices:
        result = calculate_pricing(
            car_price=base_car_price,
            option_price=option_price,
            fuel_type="전기",
            subsidy_national=80,
            company="현대"
        )
        
        base_fee = result["fees"]["fee_return_36m"]
        with_option_fee = result["fees"]["fee_return_options_36m"]
        difference = with_option_fee - base_fee
        
        print(f"{option_price:>10,}원 {base_fee:>13,}원 {with_option_fee:>13,}원 {difference:>8,}원")


def example_subsidy_impact():
    """보조금 영향 분석 예시"""
    print("\n💰 보조금 영향 분석")
    print("="*50)
    
    base_car_price = 50000000
    subsidies = [0, 40, 60, 80, 100]  # 만원 단위
    
    print(f"차량 가격: {base_car_price:,}원")
    print(f"{'보조금':<8} {'총차량비용':<15} {'36개월 반납형':<15}")
    print("-" * 40)
    
    for subsidy in subsidies:
        result = quick_calculate(
            car_price=base_car_price,
            fuel_type="전기",
            subsidy_national=subsidy,
            company="현대"
        )
        
        print(f"{subsidy:>6}만원 {result['총차량비용']:>13,}원 {result['36개월_반납형']:>13,}원")


def example_core_api_usage():
    """Core API 직접 사용 예시"""
    print("\n🔧 Core API 직접 사용 예시")
    print("="*50)
    
    # Core API 직접 사용
    result = calculate_pricing_complete(
        car_price=48000000,
        option_price=1800000,
        fuel_type="전기",
        subsidy_national=80,
        subsidy_lease=0,
        company="현대"
    )
    
    print("Core API 결과:")
    print(f"  차량 비용 상세: {result.car_cost_detail}")
    print(f"  총 차량 비용: {result.total_car_cost:,}원")
    print(f"  케어 비용: {result.care_fee:,}원/월")
    print("\n주요 구독료:")
    for key, value in result.subscription_fees.items():
        if "36m" in key:  # 36개월 요금만 출력
            print(f"  {key}: {value:,}원")


if __name__ == "__main__":
    # 모든 예시 실행
    example_basic_usage()
    example_detailed_calculation()
    example_multiple_scenarios()
    example_option_impact()
    example_subsidy_impact()
    example_core_api_usage()
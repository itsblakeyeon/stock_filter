#!/usr/bin/env python3
"""
옵션 프라이싱 모듈
price_options을 기반으로 fee_options_12m부터 fee_options_84m까지 계산
"""

import pandas as pd
import math
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.config.constants import OptionConfig, YEAR_INFO



def calculate_option_fees(price_options):
    """
    옵션 프라이싱 로직을 구현할 함수
    """
    # 각 기간별 discount 합계 계산
    discount_sums = {}
    for i in range(1, 8):  # Y1부터 Y7까지
        year_key = f"Y{i}"
        term = YEAR_INFO[year_key]["term"]
        discount_sum = sum(YEAR_INFO[f"Y{j}"]["discount"] for j in range(1, i + 1))
        discount_sums[term] = discount_sum
    
    # 각 기간별 옵션 요금 계산
    option_fees = {}
    for term, discount_sum in discount_sums.items():
        fee = price_options * (1 + OptionConfig.PREMIUM_RATE) / discount_sum / 12
        # 3번째 자리에서 라운드업 (1000원 단위)
        option_fees[f"fee_options_{term}m"] = math.ceil(fee / 1000) * 1000
    
    return option_fees


def test_option_pricing():
    """
    테스트 함수 - 530,000원 옵션으로 계산
    """
    price_options = 530000
    print(f"옵션 비용: {price_options:,}원")
    print(f"Premium: {OptionConfig.PREMIUM_RATE * 100}%")
    print("-" * 50)
    
    fees = calculate_option_fees(price_options)
    
    for fee_name, fee_value in fees.items():
        print(f"{fee_name}: {fee_value:,}원")
    
    print("-" * 50)
    print("계산 공식:")
    print("fee = price_options * (1 + premium) / SUM(discounts) / 12")
    print()
    
    # 각 기간별 discount 합계도 출력
    for i in range(1, 8):
        year_key = f"Y{i}"
        term = YEAR_INFO[year_key]["term"]
        discount_sum = sum(YEAR_INFO[f"Y{j}"]["discount"] for j in range(1, i + 1))
        print(f"{term}개월: SUM(Y1~Y{i} discount) = {discount_sum:.2f}")


if __name__ == "__main__":
    print("옵션 프라이싱 모듈 준비 완료")
    print()
    test_option_pricing()

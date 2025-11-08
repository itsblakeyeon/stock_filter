#!/usr/bin/env python3
"""
구독료 계산기 (반납형/인수형 12개월)
사용법: python utils/fee_calculator.py [가격1] [가격2] ...
예시: python utils/fee_calculator.py 20340000 23550000 25230000
"""

import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pricing.pricing import calculate_subscription_fees, calculate_option_fees


def calculate_fees(price):
    """단일 가격에 대한 반납형/인수형 12개월 요금 계산"""
    # 기본 차량 (전기차 아님, 보조금 없음, 회사 미지정)
    fees = calculate_subscription_fees(price, "", "", "")

    return fees["fee_return_12m"], fees["fee_purchase_12m"]


def interactive_mode():
    """대화형 모드"""
    print("=== Fee Calculator 대화형 모드 ===")
    print("종료하려면 'q' 입력\n")

    while True:
        try:
            user_input = input("차량 가격을 입력하세요 (예: 20340000): ").strip()

            if user_input.lower() == "q":
                print("종료합니다.")
                break

            price = int(user_input.replace(",", ""))
            return_fee, purchase_fee = calculate_fees(price)

            print(f"\n차량 가격: {price:,}원")
            print(f"반납형 12개월: {return_fee:,}원")
            print(f"인수형 12개월: {purchase_fee:,}원")
            print("-" * 40 + "\n")

        except ValueError:
            print("올바른 숫자를 입력해주세요.\n")
        except KeyboardInterrupt:
            print("\n종료합니다.")
            break


def main():
    if len(sys.argv) < 2:
        # 인수가 없으면 대화형 모드로 실행
        interactive_mode()
        return

    prices = []
    for arg in sys.argv[1:]:
        try:
            price = int(arg.replace(",", ""))
            prices.append(price)
        except ValueError:
            print(f"잘못된 가격 형식: {arg}")
            sys.exit(1)

    print("=== 구독료 계산 결과 ===\n")

    for price in prices:
        return_fee, purchase_fee = calculate_fees(price)
        print(f"차량 가격: {price:,}원")
        print(f"반납형 12개월: {return_fee:,}원")
        print(f"인수형 12개월: {purchase_fee:,}원")
        print("-" * 40)


if __name__ == "__main__":
    main()

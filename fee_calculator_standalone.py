#!/usr/bin/env python3
"""
구독료 계산기 웹 애플리케이션 (독립 실행형)
Streamlit 기반 구독료 계산 도구
"""

import streamlit as st
import pandas as pd
import math


# 상수 정의
class PricingConfig:
    DOWN_PAYMENT_RATE = 0.3
    INTEREST_RATE = 0.049
    REGISTRATION_FEE = 300000
    ELECTRIC_TAX_SUBSIDY = 730000
    RETURN_TYPE_LOSS = 0.85
    PURCHASE_TYPE_LOSS = 0.95
    DEFAULT_CAR_PRICE = 30000000


class CostStructure:
    INITIAL_COSTS = {
        "registration": 300000,
        "insurance": 500000,
        "delivery": 100000,
        "initial_maintenance": 50000,
    }
    
    RECURRING_YEARLY_COSTS = {
        "insurance": 800000,
        "maintenance": 400000,
        "management": 100000,
    }


YEAR_INFO = {
    "Y0": {"discount": 1.0},
    "Y1": {"discount": 0.95, "troi": {"반납형": 12, "인수형": 8}},
    "Y2": {"discount": 0.90, "troi": {"반납형": 12, "인수형": 8}},
    "Y3": {"discount": 0.86, "troi": {"반납형": 12, "인수형": 8}},
    "Y4": {"discount": 0.82, "troi": {"반납형": 12, "인수형": 8}},
    "Y5": {"discount": 0.78, "troi": {"반납형": 12, "인수형": 8}},
    "Y6": {"discount": 0.74, "troi": {"반납형": 12, "인수형": 8}},
    "Y7": {"discount": 0.70, "troi": {"반납형": 12, "인수형": 8}},
}


def calculate_pmt(principal, annual_rate, months):
    """월 할부금 계산"""
    r = annual_rate / 12
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def calculate_car_cost(car_price):
    """차량 비용 계산 (기본 설정)"""
    car = {
        "car": car_price,
        "tax": car_price * 0.07,
        "rebate": -(car_price * 0.01),  # 테슬라 제외 리베이트
        "plate": PricingConfig.REGISTRATION_FEE,
        "promo": 0,
    }
    return car, sum(car.values())


def get_cost_structure():
    """비용 구조 반환"""
    return sum(CostStructure.INITIAL_COSTS.values()), sum(
        CostStructure.RECURRING_YEARLY_COSTS.values()
    )


def calculate_residual_values(car_cost):
    """잔존가치 계산"""
    depreciation_rate_5_years = 0.15
    depreciation_rate_6_years = 0.12
    
    ratios = {
        "Y1": 1 - depreciation_rate_5_years,
        "Y2": 1 - depreciation_rate_5_years * 2,
        "Y3": 1 - depreciation_rate_5_years * 3,
        "Y4": 1 - depreciation_rate_5_years * 4,
        "Y5": 1 - depreciation_rate_5_years * 5,
        "Y6": 1 - depreciation_rate_6_years * 6,
        "Y7": 1 - depreciation_rate_6_years * 7,
    }
    return {year: round(car_cost * ratio) for year, ratio in ratios.items()}


def calculate_subscription_return_fee(year_label, discounted_costs, residual_values):
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
    car_cost, down_payment, annual_rate, total_months
):
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
    n_years,
    down_payment,
    init_setup_cost,
    installment_payment_yearly,
    recurring_cost_1y,
    early_repayment_fees_by_term,
):
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
    year_label,
    down_payment,
    init_setup_cost,
    installment_payment_yearly,
    recurring_cost_1y,
    early_repayment_fees_by_term,
):
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


def calculate_subscription_fees(car_price):
    """구독료 계산 메인 함수"""
    # 차량 비용 계산
    car, car_cost = calculate_car_cost(car_price)
    down_payment = car["car"] * PricingConfig.DOWN_PAYMENT_RATE

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

    # 반납형 구독료 (12개월만)
    return_fee = calculate_subscription_return_fee(
        "Y1", discounted_costs, residual_values
    )

    # 인수형 중도상환 수수료
    early_repayment_fees = calculate_early_repayment_fees_by_term(
        car_cost, down_payment, PricingConfig.INTEREST_RATE, installment_months
    )

    # 인수형 구독료 (12개월만)
    purchase_fee = calculate_subscription_own_fee(
        "Y1",
        down_payment,
        init_setup_cost,
        installment_payment_yearly,
        recurring_cost_1y,
        early_repayment_fees,
    )

    return return_fee, purchase_fee


def calculate_fees(price):
    """단일 가격에 대한 반납형/인수형 12개월 요금 계산"""
    return calculate_subscription_fees(price)


def format_currency(amount):
    """금액을 천 단위 구분자로 포맷팅"""
    return f"{amount:,}원"


def main():
    st.set_page_config(page_title="구독료 계산기", page_icon="💰", layout="wide")

    st.title("💰 구독료 계산기")
    st.markdown("차량 가격을 입력하면 반납형과 인수형 12개월 구독료를 계산해드립니다.")
    st.markdown("---")

    # 입력 방식 선택
    input_method = st.radio(
        "입력 방식을 선택하세요:", ["단일 가격 입력", "여러 가격 입력"], horizontal=True
    )

    if input_method == "단일 가격 입력":
        # 단일 가격 입력
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("📋 가격 입력")
            price_input = st.number_input(
                "차량 가격 (원)",
                min_value=0,
                value=20340000,
                step=10000,
                format="%d",
                help="차량 가격을 원 단위로 입력하세요",
            )

            if st.button("💰 구독료 계산", type="primary"):
                if price_input > 0:
                    return_fee, purchase_fee = calculate_fees(price_input)

                    # 결과를 세션 상태에 저장
                    st.session_state.single_result = {
                        "price": price_input,
                        "return_fee": return_fee,
                        "purchase_fee": purchase_fee,
                    }

        with col2:
            st.subheader("📊 계산 결과")
            if "single_result" in st.session_state:
                result = st.session_state.single_result

                st.success(f"**차량 가격: {format_currency(result['price'])}**")

                col_return, col_purchase = st.columns(2)
                with col_return:
                    st.metric(
                        "반납형 12개월",
                        format_currency(result["return_fee"]),
                        help="반납형 구독료 (12개월)",
                    )

                with col_purchase:
                    st.metric(
                        "인수형 12개월",
                        format_currency(result["purchase_fee"]),
                        help="인수형 구독료 (12개월)",
                    )
            else:
                st.info("차량 가격을 입력하고 계산 버튼을 눌러주세요.")

    else:
        # 여러 가격 입력
        st.subheader("📋 여러 가격 입력")

        col1, col2 = st.columns([1, 2])

        with col1:
            prices_text = st.text_area(
                "차량 가격들 (한 줄에 하나씩)",
                placeholder="20340000\n23550000\n25230000",
                height=200,
                help="차량 가격을 한 줄에 하나씩 입력하세요. 쉼표는 자동으로 제거됩니다.",
            )

            if st.button("💰 일괄 계산", type="primary"):
                if prices_text.strip():
                    try:
                        # 입력된 텍스트를 줄 단위로 분할하고 숫자로 변환
                        price_lines = [
                            line.strip()
                            for line in prices_text.strip().split("\n")
                            if line.strip()
                        ]
                        prices = []

                        for line in price_lines:
                            # 쉼표 제거 후 숫자로 변환
                            clean_price = line.replace(",", "").replace(" ", "")
                            if clean_price.isdigit():
                                prices.append(int(clean_price))

                        if prices:
                            # 각 가격에 대해 계산
                            results = []
                            for price in prices:
                                return_fee, purchase_fee = calculate_fees(price)
                                results.append(
                                    {
                                        "차량가격": price,
                                        "반납형_12개월": return_fee,
                                        "인수형_12개월": purchase_fee,
                                    }
                                )

                            # 결과를 세션 상태에 저장
                            st.session_state.multiple_results = results

                        else:
                            st.error("유효한 가격을 입력해주세요.")

                    except Exception as e:
                        st.error(f"입력 처리 중 오류가 발생했습니다: {str(e)}")

        with col2:
            st.subheader("📊 계산 결과")
            if "multiple_results" in st.session_state:
                results = st.session_state.multiple_results

                # DataFrame으로 변환하여 표시
                df = pd.DataFrame(results)

                # 금액 포맷팅
                df_display = df.copy()
                df_display["차량가격"] = df_display["차량가격"].apply(
                    lambda x: f"{x:,}원"
                )
                df_display["반납형_12개월"] = df_display["반납형_12개월"].apply(
                    lambda x: f"{x:,}원"
                )
                df_display["인수형_12개월"] = df_display["인수형_12개월"].apply(
                    lambda x: f"{x:,}원"
                )

                st.dataframe(df_display, use_container_width=True, hide_index=True)

                # 요약 통계
                st.markdown("##### 📈 요약")
                col_count, col_avg_return, col_avg_purchase = st.columns(3)

                with col_count:
                    st.metric("계산된 차량 수", f"{len(results)}대")

                with col_avg_return:
                    avg_return = sum(r["반납형_12개월"] for r in results) // len(
                        results
                    )
                    st.metric("반납형 평균", format_currency(avg_return))

                with col_avg_purchase:
                    avg_purchase = sum(r["인수형_12개월"] for r in results) // len(
                        results
                    )
                    st.metric("인수형 평균", format_currency(avg_purchase))

            else:
                st.info("차량 가격들을 입력하고 계산 버튼을 눌러주세요.")

    # 하단 정보
    st.markdown("---")
    with st.expander("ℹ️ 계산 정보"):
        st.markdown(
            """
        **계산 조건:**
        - 전기차 아님 (일반 연료)
        - 보조금 없음
        - 회사 미지정 (테슬라 제외)
        - 옵션 가격 0원
        
        **구독료 유형:**
        - **반납형**: 계약 종료 시 차량 반납
        - **인수형**: 계약 종료 시 차량 인수 가능
        """
        )


if __name__ == "__main__":
    main()
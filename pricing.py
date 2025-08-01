#!/usr/bin/env python3
import pandas as pd
import math

# 설정
PARAMS = {
    "금리": 0.11,
    "감가율_5년차이하": 0.13,
    "감가율_6년차이상": 0.12,
    "선수율": 0.20,
    "반납형_대손": 1.02,
    "인수형_대손": 1.02,
}

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


def calculate_pmt(principal, annual_rate, months):
    r = annual_rate / 12
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def calculate_car_cost(car_price):
    car = {
        "car": car_price,
        "tax": car_price * 0.07,
        "subsidy_national": 0,
        "subsidy_lease": 0,
        "subsidy_tax": 0,
        "plate": 200000,
        "promo": 0,
    }
    return car, sum(car.values())


def get_cost_structure():
    init_setup = {
        "adv": 1500000,
        "blackbox": 50000,
        "tint_highpass": 60000,
        "delivery": 200000,
        "misc": 10000,
    }
    recurring_1y = {"labor": 600000, "car_tax": 720000, "monitoring": 132000}
    return sum(init_setup.values()), sum(recurring_1y.values())


def calculate_residual_values(car_cost):
    ratios = {
        "Y1": 1 - PARAMS["감가율_5년차이하"],
        "Y2": 1 - PARAMS["감가율_5년차이하"] * 2,
        "Y3": 1 - PARAMS["감가율_5년차이하"] * 3,
        "Y4": 1 - PARAMS["감가율_5년차이하"] * 4,
        "Y5": 1 - PARAMS["감가율_5년차이하"] * 5,
        "Y6": 1 - PARAMS["감가율_6년차이상"] * 6,
        "Y7": 1 - PARAMS["감가율_6년차이상"] * 7,
    }
    return {year: round(car_cost * ratio) for year, ratio in ratios.items()}


def calculate_subscription_return_fee(year_label, discounted_costs, residual_values):
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

    subscription_fee = (numerator / denominator) * PARAMS["반납형_대손"] / 10000
    return math.ceil(subscription_fee) * 10000


def calculate_early_repayment_fees_by_term(
    car_cost, down_payment, annual_rate, total_months
):
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

    subscription_fee = (numerator / denominator) * PARAMS["인수형_대손"] / 10000
    return math.ceil(subscription_fee) * 10000


def calculate_subscription_fees(car_price, care_service_monthly=50000):
    # 차량 비용 계산
    car, car_cost = calculate_car_cost(car_price)
    down_payment = car["car"] * PARAMS["선수율"]

    # 할부금 계산
    installment_months = 60
    monthly_payment = calculate_pmt(
        car_cost - down_payment, PARAMS["금리"], installment_months
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
    for year_label in YEAR_INFO:
        if year_label == "Y0":
            continue
        term = YEAR_INFO[year_label]["term"]
        fee = calculate_subscription_return_fee(
            year_label, discounted_costs, residual_values
        )
        return_fees[f"반납형_{term}개월"] = fee

    # 인수형 중도상환 수수료
    early_repayment_fees = calculate_early_repayment_fees_by_term(
        car_cost, down_payment, PARAMS["금리"], installment_months
    )

    # 인수형 구독료
    own_fees = {}
    for year_label in YEAR_INFO:
        if year_label == "Y0":
            continue
        term = YEAR_INFO[year_label]["term"]
        fee = calculate_subscription_own_fee(
            year_label,
            down_payment,
            init_setup_cost,
            installment_payment_yearly,
            recurring_cost_1y,
            early_repayment_fees,
        )
        own_fees[f"인수형_{term}개월"] = fee

    # 케어서비스 포함
    return_fees_care = {}
    own_fees_care = {}

    for key, fee in return_fees.items():
        # "반납형_12개월" -> "반납형_케어_12개월"
        term = key.split("_")[-1]  # "12개월"
        return_fees_care[f"반납형_케어_{term}"] = fee + care_service_monthly

    for key, fee in own_fees.items():
        # "인수형_12개월" -> "인수형_케어_12개월"
        term = key.split("_")[-1]  # "12개월"
        own_fees_care[f"인수형_케어_{term}"] = fee + care_service_monthly

    return {**return_fees, **own_fees, **return_fees_care, **own_fees_care}


def calculate_pricing(df):
    """전처리된 데이터에 구독료를 계산하는 함수"""
    print("구독료 계산 시작...")

    # 구독료 계산
    subscription_columns = []
    for idx, row in df.iterrows():
        if idx % 50 == 0:
            print(f"  {idx+1}/{len(df)} 차량 처리 중...")

        car_price = float(row["가격"])
        if pd.isna(car_price) or car_price <= 0:
            car_price = 39510000.0

        fees = calculate_subscription_fees(car_price)

        for fee_name, fee_value in fees.items():
            if fee_name not in subscription_columns:
                subscription_columns.append(fee_name)
                df[fee_name] = 0
            df.at[idx, fee_name] = fee_value

    print(f"✅ 구독료 계산 완료! {len(subscription_columns)}개 구독료 컬럼")
    return df


if __name__ == "__main__":
    # 테스트용 실행
    from cleansing import clean_data

    df = clean_data()
    result_df = calculate_pricing(df)
    print(f"계산된 구독료 컬럼: {list(result_df.columns[-28:])}")

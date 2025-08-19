#!/usr/bin/env python3
import pandas as pd
import math
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.pricing.price_reference import (
    get_all_subsidy_data,
    find_price_by_trim,
    find_price_by_key,
)
from src.config.constants import (
    PricingConfig,
    YEAR_INFO,
    SUBSCRIPTION_TERMS,
    CostStructure,
)

# 기존 코드와의 호환성을 위해 data 변수 생성
subsidy_data = get_all_subsidy_data()


def calculate_pmt(principal, annual_rate, months):
    """월 할부금 계산"""
    r = annual_rate / 12
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def match_subsidy(subsidy_trim):
    """subsidy_트림을 기반으로 보조금 정보를 매칭하는 함수"""
    if not subsidy_trim or subsidy_trim == "":
        return 0, 0

    # subsidy.py의 데이터에서 매칭
    for row in subsidy_data:
        if row[1] == subsidy_trim:  # trim 컬럼 매칭
            return row[2], row[3]  # 국비 보조금, 리스 보조금

    return 0, 0


def add_subsidy_columns_to_df(df):
    """데이터프레임에 보조금 정보 컬럼을 추가하는 함수 (최적화 버전)"""
    print("💰 보조금 정보 매칭 중...")

    # 보조금 데이터를 DataFrame으로 변환
    subsidy_df = pd.DataFrame(subsidy_data, columns=["company", "trim", "national", "lease"])  # type: ignore

    if not subsidy_df.empty:
        # key_subsidy로 매칭
        merged_df = df.merge(
            subsidy_df[["trim", "national", "lease"]],
            left_on="key_subsidy",
            right_on="trim",
            how="left",
        )

        # 매칭된 보조금 정보 복사 (보조금은 차감되므로 음수로 저장)
        df["subsidy_national"] = -(
            merged_df["national"].fillna(0) * 10000
        )  # 음수로 변환
        df["subsidy_lease"] = -(merged_df["lease"].fillna(0) * 10000)  # 음수로 변환

        # 전기차 세금 보조금
        df["subsidy_tax"] = df["fuel"].apply(
            lambda x: -PricingConfig.ELECTRIC_TAX_SUBSIDY if x == "전기" else 0
        )
    else:
        # 기본값 설정
        df["subsidy_national"] = 0
        df["subsidy_lease"] = 0
        df["subsidy_tax"] = df["fuel"].apply(
            lambda x: -PricingConfig.ELECTRIC_TAX_SUBSIDY if x == "전기" else 0
        )

    print(f"✅ 보조금 정보 매칭 완료: {len(df)}개 차량")
    return df


def match_price_info(model, trim, year=None):
    """모델, 트림, 연식을 기반으로 가격 정보를 매칭하는 함수"""
    if not model or not trim or model == "" or trim == "":
        return {"price_car_pre": "?", "price_car_post": "?"}

    try:
        price_info = find_price_by_trim(model, trim, year)
        if price_info:
            return {
                "price_car_pre": price_info.get("price_car_pre", ""),
                "price_car_post": price_info.get("price_car_post", ""),
            }
        else:
            return {"price_car_pre": "?", "price_car_post": "?"}
    except Exception as e:
        return {"price_car_pre": "?", "price_car_post": "?"}


def add_price_columns_to_df(df):
    """데이터프레임에 가격 정보 컬럼을 추가하는 함수 (벡터화된 Key 필드 매칭)"""
    print("💰 가격 정보 매칭 중...")

    # 가격 컬럼 추가
    df["price_car_tax_pre"] = "?"
    df["price_car_tax_post"] = "?"

    # key_admin 필드가 있는지 확인
    if "key_admin" in df.columns:
        # 가격 참조 데이터 로드
        from src.pricing.price_reference import get_price_data

        price_df = get_price_data()

        if not price_df.empty and "key" in price_df.columns:
            # key_admin 필드로 벡터화된 매칭
            merged_df = df.merge(
                price_df[["key", "price_car_pre", "price_car_post"]],
                left_on="key_admin",
                right_on="key",
                how="left",
            )

            # 매칭된 가격 정보 복사
            df["price_car_tax_pre"] = merged_df["price_car_pre"].fillna("?")
            df["price_car_tax_post"] = merged_df["price_car_post"].fillna("?")
        else:
            print("⚠️ 가격 참조 데이터에 Key 필드가 없습니다.")
    else:
        # 기존 방식 (모델, 트림, 연식 개별 매칭)
        for idx, row in df.iterrows():
            model = row.get("model", "")
            trim = row.get("trim", "")
            year = row.get("year", "")

            price_info = match_price_info(model, trim, year)
            if price_info:
                df.at[idx, "price_car_tax_pre"] = price_info["price_car_pre"]
                df.at[idx, "price_car_tax_post"] = price_info["price_car_post"]

    print(f"✅ 가격 정보 매칭 완료: {len(df)}개 차량")
    return df


def calculate_car_cost(car_price, fuel_type="", subsidy_trim="", company=""):
    """차량 비용 계산"""
    # 보조금 계산
    subsidy_national, subsidy_lease = match_subsidy(subsidy_trim)
    subsidy_tax = PricingConfig.ELECTRIC_TAX_SUBSIDY if fuel_type == "전기" else 0
    
    # 리베이트 계산 (테슬라 제외)
    rebate = -(car_price * 0.01) if str(company).strip() != "테슬라" else 0

    car = {
        "car": car_price,
        "tax": car_price * 0.07,
        "subsidy_national": -(subsidy_national * 10000),  # 보조금은 차감(-)
        "subsidy_lease": -(subsidy_lease * 10000),  # 보조금은 차감(-)
        "subsidy_tax": -subsidy_tax,  # 보조금은 차감(-)
        "rebate": rebate,  # 리베이트 추가
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


def calculate_option_fees(price_options):
    """옵션 프라이싱 계산 함수 (12, 36, 60, 84개월만)"""
    # 필요한 기간만 계산
    required_terms = [12, 36, 60, 84]

    # 각 기간별 discount 합계 계산
    discount_sums = {}
    for term in required_terms:
        # term에 해당하는 year 찾기
        year_count = 0
        if term == 12:
            year_count = 1
        elif term == 36:
            year_count = 3
        elif term == 60:
            year_count = 5
        elif term == 84:
            year_count = 7

        discount_sum = sum(
            YEAR_INFO[f"Y{j}"]["discount"] for j in range(1, year_count + 1)
        )
        discount_sums[term] = discount_sum

    # 각 기간별 옵션 요금 계산
    option_fees = {}
    for term, discount_sum in discount_sums.items():
        fee = price_options * 1.5 / discount_sum / 12  # premium 50%
        # 3번째 자리에서 라운드업 (1000원 단위)
        option_fees[f"fee_options_{term}m"] = math.ceil(fee / 1000) * 1000

    return option_fees


def calculate_subscription_fees(car_price, fuel_type="", subsidy_trim="", company=""):
    """구독료 계산 메인 함수"""
    # 차량 비용 계산
    car, car_cost = calculate_car_cost(car_price, fuel_type, subsidy_trim, company)
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

    # 반납형 구독료 (12, 36, 60, 84개월만)
    return_fees = {}
    required_terms = [12, 36, 60, 84]

    for term in required_terms:
        # term에 해당하는 year 찾기
        year_count = 0
        if term == 12:
            year_count = 1
        elif term == 36:
            year_count = 3
        elif term == 60:
            year_count = 5
        elif term == 84:
            year_count = 7

        year_label = f"Y{year_count}"
        fee = calculate_subscription_return_fee(
            year_label, discounted_costs, residual_values
        )
        return_fees[f"fee_return_{term}m"] = fee

    # 인수형 중도상환 수수료
    early_repayment_fees = calculate_early_repayment_fees_by_term(
        car_cost, down_payment, PricingConfig.INTEREST_RATE, installment_months
    )

    # 인수형 구독료 (12, 36, 60, 84개월만)
    own_fees = {}
    for term in required_terms:
        # term에 해당하는 year 찾기
        year_count = 0
        if term == 12:
            year_count = 1
        elif term == 36:
            year_count = 3
        elif term == 60:
            year_count = 5
        elif term == 84:
            year_count = 7

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


def calculate_pricing(df):
    """전처리된 데이터에 모든 가격 관련 계산을 적용하는 함수"""
    print("💰 가격 계산 시작...")

    # 1. 보조금 정보 매칭
    df = add_subsidy_columns_to_df(df)

    # 2. 가격 정보 매칭
    df = add_price_columns_to_df(df)

    # 3. 차량 비용 계산
    # price_car_tax_post가 "?"인 경우 price_car_original 사용
    df["price_tax"] = df.apply(
        lambda row: (
            float(row["price_car_tax_post"])
            if pd.notna(row["price_car_tax_post"]) and row["price_car_tax_post"] != "?"
            else float(row["price_car_original"])
        )
        * 0.07,
        axis=1,
    )
    df["price_registration"] = PricingConfig.REGISTRATION_FEE
    df["rebate"] = df.apply(
        lambda row: -(
            float(row["price_car_tax_post"])
            if pd.notna(row["price_car_tax_post"]) and row["price_car_tax_post"] != "?"
            else float(row["price_car_original"])
        )
        * 0.01 if str(row.get("company", "")).strip() != "테슬라" else 0,
        axis=1,
    )
    df["promotion"] = 0
    df["price_total"] = df.apply(
        lambda row: (
            float(row["price_car_tax_post"])
            if pd.notna(row["price_car_tax_post"]) and row["price_car_tax_post"] != "?"
            else float(row["price_car_original"])
        )
        + row["price_tax"]
        + row["subsidy_national"]
        + row["subsidy_lease"]
        + row["subsidy_tax"]
        + row["rebate"]
        + PricingConfig.REGISTRATION_FEE,
        axis=1,
    )

    # 3-1. 옵션 가격 계산 (price_car_original - price_car_tax_pre)
    print("💰 옵션 가격 계산 중...")
    df["price_options"] = "?"
    for idx, row in df.iterrows():
        try:
            # price_car_tax_pre가 "?"면 계산 불가
            if pd.isna(row["price_car_tax_pre"]) or row["price_car_tax_pre"] == "?":
                df.at[idx, "price_options"] = "?"
                continue

            price_car_original = (
                float(row["price_car_original"])
                if pd.notna(row["price_car_original"])
                and row["price_car_original"] != "?"
                else 0
            )
            price_car_tax_pre = float(row["price_car_tax_pre"])
            df.at[idx, "price_options"] = max(0, price_car_original - price_car_tax_pre)
        except (ValueError, TypeError):
            df.at[idx, "price_options"] = "?"
    print(f"✅ 옵션 가격 계산 완료: {len(df)}개 차량")

    # 4. 구독료 계산
    print("구독료 계산 시작...")
    subscription_columns = []
    for idx, row in df.iterrows():
        if idx % 50 == 0:
            print(f"  {idx+1}/{len(df)} 차량 처리 중...")

        car_price = (
            float(row["price_car_tax_post"])
            if pd.notna(row["price_car_tax_post"]) and row["price_car_tax_post"] != "?"
            else float(row["price_car_original"])
        )
        if pd.isna(car_price) or car_price <= 0:
            car_price = PricingConfig.DEFAULT_CAR_PRICE

        # 보조금 정보 가져오기
        fuel_type = str(row["fuel"]) if pd.notna(row["fuel"]) else ""
        subsidy_trim = str(row["key_subsidy"]) if pd.notna(row["key_subsidy"]) else ""
        company = str(row["company"]) if pd.notna(row["company"]) else ""

        fees = calculate_subscription_fees(car_price, fuel_type, subsidy_trim, company)

        for fee_name, fee_value in fees.items():
            if fee_name not in subscription_columns:
                subscription_columns.append(fee_name)
                df[fee_name] = 0
            df.at[idx, fee_name] = fee_value

    # 4-1. 옵션 프라이싱 계산
    print("옵션 프라이싱 계산 시작...")
    option_columns = []
    for idx, row in df.iterrows():
        if idx % 50 == 0:
            print(f"  {idx+1}/{len(df)} 차량 옵션 처리 중...")

        # price_options이 유효한 값인지 확인
        price_options = row.get("price_options", 0)
        if pd.isna(price_options) or price_options == "?" or price_options == 0:
            # 옵션 요금을 0으로 설정 (12, 36, 60, 84개월만)
            for term in [12, 36, 60, 84]:
                fee_name = f"fee_options_{term}m"
                if fee_name not in option_columns:
                    option_columns.append(fee_name)
                    df[fee_name] = 0
                df.at[idx, fee_name] = 0
        else:
            try:
                price_options = float(price_options)
                option_fees = calculate_option_fees(price_options)

                for fee_name, fee_value in option_fees.items():
                    if fee_name not in option_columns:
                        option_columns.append(fee_name)
                        df[fee_name] = 0
                    df.at[idx, fee_name] = fee_value
            except (ValueError, TypeError):
                # 옵션 요금을 0으로 설정
                for term in [12, 24, 36, 48, 60, 72, 84]:
                    fee_name = f"fee_options_{term}m"
                    if fee_name not in option_columns:
                        option_columns.append(fee_name)
                        df[fee_name] = 0
                    df.at[idx, fee_name] = 0

    # 5. 옵션이 포함된 구독료 필드 생성 (12, 36, 60, 84개월만)
    print("💰 옵션 포함 구독료 계산 중...")
    terms = [12, 36, 60, 84]

    for term in terms:
        # 반납형 + 옵션
        return_col = f"fee_return_{term}m"
        options_col = f"fee_options_{term}m"
        return_options_col = f"fee_return_options_{term}m"

        if return_col in df.columns and options_col in df.columns:
            df[return_options_col] = df[return_col] + df[options_col]

        # 인수형 + 옵션
        purchase_col = f"fee_purchase_{term}m"
        purchase_options_col = f"fee_purchase_options_{term}m"

        if purchase_col in df.columns and options_col in df.columns:
            df[purchase_options_col] = df[purchase_col] + df[options_col]

    print(f"✅ 구독료 계산 완료! {len(subscription_columns)}개 구독료 컬럼")

    # 6. 추가 필드 생성 (옵션 포함 구독료 계산 후)
    df["fee_care"] = df["fuel"].apply(
        lambda x: (
            PricingConfig.CARE_FEE_ELECTRIC
            if x == "전기"
            else PricingConfig.CARE_FEE_OTHER
        )
    )
    df["fee_list"] = df["fee_return_options_12m"]

    print("✅ 가격 계산 완료!")
    return df

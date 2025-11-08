#!/usr/bin/env python3
"""
구독료 계산기 웹 애플리케이션
Streamlit 기반 구독료 계산 도구
"""

import streamlit as st
import sys
import os
import pandas as pd

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pricing.pricing import calculate_subscription_fees


def calculate_fees(price):
    """단일 가격에 대한 반납형/인수형 12개월 요금 계산"""
    # 기본 차량 (전기차 아님, 보조금 없음, 회사 미지정)
    fees = calculate_subscription_fees(price, "", "", "")
    return fees["fee_return_12m"], fees["fee_purchase_12m"]


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

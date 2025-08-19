#!/usr/bin/env python3
"""
Streamlit 웹 애플리케이션
재고 데이터 처리를 위한 웹 인터페이스
"""

import streamlit as st
import sys
import os
import tempfile
import pandas as pd
from datetime import datetime
import io

# src 폴더를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.cleansing.cleansing_unified import clean_all_data
from src.pricing.pricing_unified import main as pricing_main
from src.listing.listing_unified import main as listing_main
from src.config.constants import (
    FINAL_COLUMN_ORDER,
    DataProcessing,
    get_today_date_string,
    set_global_date,
)

# run.py의 함수들 import
from run import (
    reorder_columns,
    remove_korean_subsidy_columns,
    process_final_data,
)


def create_download_file(df, filename_prefix, date_str):
    """DataFrame을 Excel 파일로 변환하여 다운로드용 바이너리 데이터 생성"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output.getvalue()


def save_uploaded_file(uploaded_file, temp_dir, target_filename):
    """업로드된 파일을 임시 디렉토리에 저장"""
    temp_path = os.path.join(temp_dir, target_filename)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path


def main():
    st.set_page_config(
        page_title="재고 데이터 처리 시스템", page_icon="🚗", layout="wide"
    )

    st.title("🚗 재고 데이터 통합 처리 시스템")
    st.markdown("---")

    # 사이드바 - 설정
    with st.sidebar:
        st.header("📋 처리 설정")

        # 날짜 선택
        today = datetime.now()
        selected_date = st.date_input(
            "처리 날짜 선택", value=today, help="데이터 처리에 사용할 날짜를 선택하세요"
        )
        date_str = selected_date.strftime("%y%m%d")

        st.info(f"선택된 날짜: {date_str}")

    # 메인 영역
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📁 현대 재고 파일")
        hyundai_file = st.file_uploader(
            "현대 재고리스트 파일 업로드 (.xlsx)",
            type=["xlsx"],
            key="hyundai",
            help="재고리스트_현대_YYMMDD.xlsx 파일을 업로드하세요",
        )

    with col2:
        st.subheader("📁 기아 재고 파일")
        kia_file = st.file_uploader(
            "기아 재고리스트 파일 업로드 (.xls)",
            type=["xls"],
            key="kia",
            help="재고리스트_기아_YYMMDD.xls 파일을 업로드하세요",
        )

    # 처리 버튼
    if st.button("🚀 데이터 처리 시작", type="primary", use_container_width=True):
        if hyundai_file is None or kia_file is None:
            st.error("❌ 현대와 기아 재고 파일을 모두 업로드해주세요.")
            return

        try:
            with st.spinner("📋 데이터 처리 중..."):
                # 임시 디렉토리 생성
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 업로드된 파일들을 임시 디렉토리에 저장
                    hyundai_path = save_uploaded_file(
                        hyundai_file, temp_dir, f"재고리스트_현대_{date_str}.xlsx"
                    )
                    kia_path = save_uploaded_file(
                        kia_file, temp_dir, f"재고리스트_기아_{date_str}.xls"
                    )

                    # 원본 data/raw 경로 백업
                    original_raw_path = "data/raw"

                    # 임시적으로 constants의 파일 경로를 업로드된 파일로 변경
                    import src.config.constants as constants

                    original_get_hyundai_raw_file = (
                        constants.FilePaths.get_hyundai_raw_file
                    )
                    original_get_kia_raw_file = constants.FilePaths.get_kia_raw_file

                    # 임시 파일 경로로 override
                    constants.FilePaths.get_hyundai_raw_file = (
                        lambda date_str=None: hyundai_path
                    )
                    constants.FilePaths.get_kia_raw_file = (
                        lambda date_str=None: kia_path
                    )

                    try:
                        # 전역 날짜 설정
                        set_global_date(date_str)

                        # 진행 상황 표시
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        # 1. 통합 클렌징
                        status_text.text("📋 1단계: 통합 클렌징 진행 중...")
                        progress_bar.progress(25)
                        cleaned_df = clean_all_data()
                        st.success(f"✅ 클렌징 완료: {len(cleaned_df)}대")

                        # 2. 통합 프라이싱
                        status_text.text("📋 2단계: 통합 프라이싱 진행 중...")
                        progress_bar.progress(50)
                        priced_df = pricing_main(cleaned_df)
                        st.success(f"✅ 프라이싱 완료: {len(priced_df)}대")

                        # 3. 통합 리스팅
                        status_text.text("📋 3단계: 통합 리스팅 진행 중...")
                        progress_bar.progress(75)
                        listed_df = listing_main(priced_df)
                        st.success(f"✅ 리스팅 완료")

                        # 4. 최종 파일 생성
                        status_text.text("📋 4단계: 최종 파일 생성 중...")
                        progress_bar.progress(90)

                        # 선택된 결과 (재고 조건 이상)
                        df_selected = reorder_columns(listed_df)

                        # 전체 결과
                        df_all = process_final_data(cleaned_df)

                        # 업로드용 결과
                        selected_columns = [
                            "code_sales_a",
                            "code_sales_b",
                            "code_color_a",
                            "code_color_b",
                            "request",
                            "stock",
                            "image_thumbnail",
                            "image_detail",
                            "company",
                            "model",
                            "trim",
                            "year",
                            "fuel",
                            "options",
                            "wheel_tire",
                            "color_exterior",
                            "color_interior",
                            "price_total",
                            "price_options",
                            "fee_list",
                            "fee_care",
                            "fee_return_options_12m",
                            "fee_return_options_36m",
                            "fee_return_options_60m",
                            "fee_return_options_84m",
                            "fee_purchase_options_12m",
                            "fee_purchase_options_36m",
                            "fee_purchase_options_60m",
                            "fee_purchase_options_84m",
                        ]
                        available_columns = [
                            col for col in selected_columns if col in listed_df.columns
                        ]
                        df_upload = listed_df[available_columns]

                        progress_bar.progress(100)
                        status_text.text("✅ 모든 처리 완료!")

                        # 결과 표시
                        st.markdown("---")
                        st.subheader("📊 처리 결과")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "선택된 차량",
                                f"{len(df_selected)}대",
                                f"재고 {DataProcessing.STOCK_THRESHOLD} 이상",
                            )
                        with col2:
                            st.metric("전체 차량", f"{len(df_all)}대", "모든 차량")
                        with col3:
                            st.metric(
                                "업로드용",
                                f"{len(df_upload)}대",
                                f"{len(df_upload.columns)}개 컬럼",
                            )

                        # 다운로드 버튼들
                        st.markdown("---")
                        st.subheader("📥 결과 파일 다운로드")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            selected_excel = create_download_file(
                                df_selected, "selected", date_str
                            )
                            st.download_button(
                                label="📋 선택된 차량 다운로드",
                                data=selected_excel,
                                file_name=f"stock_selected_{date_str}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            )

                        with col2:
                            all_excel = create_download_file(df_all, "all", date_str)
                            st.download_button(
                                label="📋 전체 차량 다운로드",
                                data=all_excel,
                                file_name=f"stock_all_{date_str}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            )

                        with col3:
                            upload_excel = create_download_file(
                                df_upload, "upload", date_str
                            )
                            st.download_button(
                                label="📋 업로드용 다운로드",
                                data=upload_excel,
                                file_name=f"stock_upload_{date_str}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            )

                        # 데이터 미리보기
                        st.markdown("---")
                        st.subheader("👀 데이터 미리보기")

                        tab1, tab2, tab3 = st.tabs(
                            ["선택된 차량", "전체 차량", "업로드용"]
                        )

                        with tab1:
                            st.dataframe(df_selected.head(10), use_container_width=True)

                        with tab2:
                            st.dataframe(df_all.head(10), use_container_width=True)

                        with tab3:
                            st.dataframe(df_upload.head(10), use_container_width=True)

                    finally:
                        # 원래 함수들 복원
                        constants.FilePaths.get_hyundai_raw_file = (
                            original_get_hyundai_raw_file
                        )
                        constants.FilePaths.get_kia_raw_file = original_get_kia_raw_file

        except Exception as e:
            st.error(f"❌ 처리 중 오류가 발생했습니다: {str(e)}")
            st.exception(e)

    # 도움말
    with st.expander("ℹ️ 사용 방법"):
        st.markdown(
            """
        1. **파일 업로드**: 현대와 기아 재고리스트 파일을 업로드하세요
        2. **날짜 선택**: 처리할 날짜를 선택하세요 (기본: 오늘)
        3. **처리 시작**: '데이터 처리 시작' 버튼을 클릭하세요
        4. **결과 다운로드**: 처리가 완료되면 결과 파일을 다운로드하세요
        
        **파일 형식**:
        - 현대: `재고리스트_현대_YYMMDD.xlsx` 파일
        - 기아: `재고리스트_기아_YYMMDD.xls` 파일
        """
        )


if __name__ == "__main__":
    main()

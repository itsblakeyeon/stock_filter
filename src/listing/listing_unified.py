#!/usr/bin/env python3
import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.cleansing.cleansing_unified import clean_all_data
from src.pricing.pricing import calculate_pricing
from src.image.image import add_image_urls





def main(cleaned_df=None):
    print("🚗 현대차 + 기아차 통합 재고 리스트 생성 시작...")
    
    # 1. 통합 데이터 전처리 (이미 제공된 경우 사용, 아니면 새로 생성)
    if cleaned_df is None:
        cleaned_df = clean_all_data()
    
    # 2. 이미지 URL 추가
    image_df = add_image_urls(cleaned_df)
    
    # 3. 프라이싱 적용 (이미 완료된 경우 사용)
    if "반납형_12개월" in image_df.columns:
        result_df = image_df
    else:
        from src.pricing.pricing_unified import main as pricing_main
        result_df = pricing_main(image_df)
    
    # 4. 재고 필터링 및 추가 조건 적용
    result_df["stock"] = pd.to_numeric(result_df["stock"], errors='coerce')
    result_df["stock"] = result_df["stock"].fillna(0).astype(int)
    
    # 기본 필터링: 재고 3 이상
    from src.config.constants import DataProcessing
    filtered_df = result_df[result_df["stock"] >= DataProcessing.STOCK_THRESHOLD].copy()
    
    # 추가 필터링 조건 적용
    # 1) 기본 휠&타이어만
    filtered_df = filtered_df[filtered_df["wheel_tire"] == "기본 휠&타이어"].copy()
    
    # 2) 기아차 특정 모델 제외 (봉고, K5, 니로, K8, K9)
    filtered_df = filtered_df[
        ~((filtered_df["company"] == "기아") & 
          (filtered_df["model"].isin(["봉고", "K5", "니로", "K8", "K9"])))
    ].copy()
    
    # 3) 빌트인캠만 포함 또는 무옵션 차량 필터링
    def filter_builtin_cam_or_no_options(df):
        def has_only_builtin_cam_or_no_options(option_str):
            if pd.isna(option_str) or option_str == "":
                return True  # 무옵션 허용 (빈 값)
            option_str = str(option_str).strip()
            if option_str == "" or option_str == "무옵션":
                return True  # 빈 문자열이나 "무옵션" 텍스트 처리
            # 빌트인캠만 있는지 확인 (쉼표로 구분된 옵션들 중 빌트인캠만 있는지)
            options = [opt.strip() for opt in option_str.split(',') if opt.strip()]
            return len(options) == 1 and "빌트인캠" in options[0]
        
        return df[df["options"].apply(has_only_builtin_cam_or_no_options)]
    
    filtered_df = filter_builtin_cam_or_no_options(filtered_df)
    
    # 5. 24, 48, 72개월 가격 컬럼 제거
    columns_to_remove = [
        "fee_return_24m", "fee_return_48m", "fee_return_72m", 
        "fee_purchase_24m", "fee_purchase_48m", "fee_purchase_72m"
    ]
    filtered_df = filtered_df.drop(columns=[col for col in columns_to_remove if col in filtered_df.columns])
    
    
    # 7. 결과 저장
    filtered_df.to_excel("data/export/stock_unified.xlsx", index=False)
    
    # 8. 회사별 통계 출력
    print(f"\n📊 회사별 통계:")
    company_stats = filtered_df["company"].value_counts()
    for company, count in company_stats.items():
        print(f"  {company}: {count}대")
    
    print(f"\n✅ 완료! {len(filtered_df)}대 차량")
    print(f"📊 필터링 조건: 재고 {DataProcessing.STOCK_THRESHOLD} 이상 + 기본 휠&타이어 + (빌트인캠만 또는 무옵션) (기아 봉고/K5/니로/K8/K9 제외)")
    print(f"📊 구독료 컬럼: {len(filtered_df.columns)-18}개")
    print(f"📁 결과 파일: data/export/stock_unified.xlsx")


if __name__ == "__main__":
    main() 
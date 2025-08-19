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
    
    # 기본 필터링: 재고 5 이상
    from src.config.constants import DataProcessing
    print(f"🔍 필터링 전: {len(result_df)}대, 컬럼 수: {len(result_df.columns)}")
    
    filtered_df = result_df[result_df["stock"] >= DataProcessing.STOCK_THRESHOLD].copy()
    print(f"🔍 재고 {DataProcessing.STOCK_THRESHOLD} 이상 필터 후: {len(filtered_df)}대")
    
    # 추가 필터링 조건 적용
    # 1) 가격 정보 있는 차량만 (price_car_tax_pre, price_car_tax_post, price_options가 ?가 아닌 것)
    def has_valid_price_info(row):
        price_pre = str(row.get("price_car_tax_pre", "?")).strip()
        price_post = str(row.get("price_car_tax_post", "?")).strip()
        price_options = str(row.get("price_options", "?")).strip()
        
        return (price_pre != "?" and price_pre != "" and pd.notna(row.get("price_car_tax_pre")) and
                price_post != "?" and price_post != "" and pd.notna(row.get("price_car_tax_post")) and
                price_options != "?" and price_options != "" and pd.notna(row.get("price_options")))
    
    # 가격 컬럼 상태 디버깅
    print(f"🔍 가격 컬럼 존재 여부:")
    print(f"  - price_car_tax_pre: {'✅' if 'price_car_tax_pre' in filtered_df.columns else '❌'}")
    print(f"  - price_car_tax_post: {'✅' if 'price_car_tax_post' in filtered_df.columns else '❌'}")  
    print(f"  - price_options: {'✅' if 'price_options' in filtered_df.columns else '❌'}")
    
    if 'price_car_tax_pre' in filtered_df.columns:
        unique_pre = filtered_df['price_car_tax_pre'].unique()[:3]
        print(f"  - price_car_tax_pre 샘플: {unique_pre}")
    
    filtered_df = filtered_df[filtered_df.apply(has_valid_price_info, axis=1)].copy()
    print(f"🔍 가격 정보 필터 후: {len(filtered_df)}대")
    
    # 2) 기본 휠&타이어만
    if len(filtered_df) > 0:
        filtered_df = filtered_df[filtered_df["wheel_tire"] == "기본 휠&타이어"].copy()
        print(f"🔍 기본 휠&타이어 필터 후: {len(filtered_df)}대")
    
    # 3) 빌트인캠만 포함하는 차량 필터링 (무옵션 제외)
    def filter_builtin_cam_only(df):
        def has_only_builtin_cam(option_str):
            if pd.isna(option_str) or option_str == "":
                return False  # 무옵션 제외
            option_str = str(option_str).strip()
            if option_str == "" or option_str == "무옵션":
                return False  # 빈 문자열이나 "무옵션" 텍스트 제외
            # 빌트인캠만 있는지 확인 (쉼표로 구분된 옵션들 중 빌트인캠만 있는지)
            options = [opt.strip() for opt in option_str.split(',') if opt.strip()]
            return len(options) == 1 and "빌트인캠" in options[0]
        
        return df[df["options"].apply(has_only_builtin_cam)]
    
    filtered_df = filter_builtin_cam_only(filtered_df)
    
    # 5. 24, 48, 72개월 가격 컬럼 제거
    columns_to_remove = [
        "fee_return_24m", "fee_return_48m", "fee_return_72m", 
        "fee_purchase_24m", "fee_purchase_48m", "fee_purchase_72m"
    ]
    filtered_df = filtered_df.drop(columns=[col for col in columns_to_remove if col in filtered_df.columns])
    
    
    # 7. 회사별 통계 출력 (안전한 처리)
    print(f"\n📊 회사별 통계:")
    if len(filtered_df) == 0:
        print("  필터링된 차량이 없습니다.")
    elif "company" not in filtered_df.columns:
        print("  company 컬럼이 존재하지 않습니다.")
    else:
        try:
            company_stats = filtered_df["company"].value_counts()
            for company, count in company_stats.items():
                print(f"  {company}: {count}대")
        except Exception as e:
            print(f"  통계 생성 실패: {e}")
    
    print(f"\n✅ 완료! {len(filtered_df)}대 차량")
    print(f"📊 필터링 조건: 재고 {DataProcessing.STOCK_THRESHOLD} 이상 + 가격정보 있음 + 기본 휠&타이어 + 빌트인캠만")
    print(f"📊 구독료 컬럼: {len(filtered_df.columns)-18}개")
    
    # 8. 필터링된 데이터 반환
    return filtered_df


if __name__ == "__main__":
    main() 
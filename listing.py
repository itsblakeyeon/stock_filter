#!/usr/bin/env python3
from cleansing import clean_data
from pricing import calculate_pricing

def main():
    print("🚗 재고 리스트 생성 시작...")
    
    # 1. 데이터 전처리
    cleaned_df = clean_data()
    
    # 2. 구독료 계산
    result_df = calculate_pricing(cleaned_df)
    
    # 3. 결과 저장
    result_df.to_excel("stock.xlsx", index=False)
    
    print(f"\n✅ 완료! {len(result_df)}대 차량, {len(result_df.columns)-12}개 구독료 컬럼")
    print(f"📁 결과 파일: listing.xlsx")

if __name__ == "__main__":
    main() 
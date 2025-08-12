#!/usr/bin/env python3
"""
통합 가격 참조 파일 생성 스크립트
subsidy 데이터와 price 데이터를 합쳐서 하나의 엑셀 파일로 생성
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
from src.pricing.price_reference import get_all_subsidy_data

# 기존 코드와의 호환성을 위해 data 변수 생성
subsidy_data = get_all_subsidy_data()

def create_price_reference():
    """통합 가격 참조 파일을 생성하는 함수"""
    print("💰 통합 가격 참조 파일 생성 시작...")
    
    # 1. Subsidy 데이터를 DataFrame으로 변환
    print("📋 보조금 데이터 처리 중...")
    subsidy_df = pd.DataFrame(subsidy_data, columns=['company', 'trim', 'subsidy_national', 'subsidy_lease'])
    subsidy_df['data_type'] = '보조금'
    subsidy_df['source'] = 'subsidy.py'
    
    # 2. Price 데이터 로드
    print("📋 가격 데이터 처리 중...")
    try:
        price_df = pd.read_excel("data/price.xlsx")
        price_df['data_type'] = '가격표'
        price_df['source'] = 'price.xlsx'
        
        # 컬럼명 정리
        price_df.columns = ['model_info', 'drive_type', 'trim', 'price_car_pre', 'price_car_post', 'data_type', 'source']
        
        print(f"✅ 가격 데이터 로드 완료: {len(price_df)}개 행")
    except Exception as e:
        print(f"⚠️ 가격 데이터 로드 실패: {e}")
        price_df = pd.DataFrame()
    
    # 3. 통합 파일 생성
    print("📋 통합 파일 생성 중...")
    
    with pd.ExcelWriter("data/reference/price_reference.xlsx", engine='openpyxl') as writer:
        # 보조금 데이터 시트
        subsidy_df.to_excel(writer, sheet_name='보조금_데이터', index=False)
        
        # 가격 데이터 시트 (있는 경우)
        if not price_df.empty:
            price_df.to_excel(writer, sheet_name='가격표_데이터', index=False)
        
        # 통합 요약 시트
        summary_data = []
        
        # 보조금 데이터 요약
        for _, row in subsidy_df.iterrows():
            summary_data.append({
                '데이터_타입': '보조금',
                '브랜드': row['company'],
                '모델/트림': row['trim'],
                '국비보조금': row['subsidy_national'],
                '리스보조금': row['subsidy_lease'],
                '출처': row['source']
            })
        
        # 가격 데이터 요약 (있는 경우)
        if not price_df.empty:
            for _, row in price_df.iterrows():
                if pd.notna(row['trim']):
                    summary_data.append({
                        '데이터_타입': '가격표',
                        '브랜드': row['model_info'] if pd.notna(row['model_info']) else '미분류',
                        '모델/트림': row['trim'],
                        '기본가격': row['price_car_pre'],
                        '세제혜택가격': row['price_car_post'],
                        '출처': row['source']
                    })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='통합_요약', index=False)
    
    print(f"✅ 통합 가격 참조 파일 생성 완료!")
    print(f"📁 파일 위치: data/reference/price_reference.xlsx")
    print(f"📊 보조금 데이터: {len(subsidy_df)}개")
    print(f"📊 가격표 데이터: {len(price_df)}개")
    print(f"📊 통합 요약: {len(summary_df)}개")
    
    return "data/reference/price_reference.xlsx"

def update_subsidy_module():
    """subsidy.py 모듈을 엑셀 파일을 읽도록 수정하는 함수"""
    print("🔄 subsidy.py 모듈 업데이트 중...")
    
    # 새로운 subsidy.py 내용 생성
    new_content = '''#!/usr/bin/env python3
"""
보조금 데이터 모듈
엑셀 파일에서 보조금 데이터를 로드
"""

import pandas as pd
import os

def load_subsidy_data():
    """보조금 데이터를 엑셀 파일에서 로드하는 함수"""
    try:
        file_path = "data/reference/price_reference.xlsx"
        if os.path.exists(file_path):
            df = pd.read_excel(file_path, sheet_name='보조금_데이터')
            return df
        else:
            print(f"⚠️ 보조금 데이터 파일을 찾을 수 없습니다: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ 보조금 데이터 로드 실패: {e}")
        return pd.DataFrame()

# 기존 코드와의 호환성을 위한 data 변수
try:
    subsidy_df = load_subsidy_data()
    if not subsidy_df.empty:
        data = subsidy_df[['company', 'trim', 'subsidy_national', 'subsidy_lease']].values.tolist()
    else:
        # 기본 데이터 (파일이 없을 경우)
        data = []
except:
    data = []

# DataFrame 생성 (기존 코드와의 호환성)
df = pd.DataFrame(data, columns=['company', 'trim', 'subsidy_national', 'subsidy_lease']) if data else pd.DataFrame()
'''
    
    # subsidy.py 파일 업데이트
    subsidy_file_path = "src/pricing/subsidy.py"
    with open(subsidy_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ subsidy.py 모듈 업데이트 완료!")

if __name__ == "__main__":
    # 1. 통합 가격 참조 파일 생성
    create_price_reference()
    
    # 2. subsidy.py 모듈 업데이트
    update_subsidy_module()
    
    print("\n🎉 모든 작업 완료!")

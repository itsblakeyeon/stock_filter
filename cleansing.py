#!/usr/bin/env python3
import pandas as pd

def clean_data():
    """재고 데이터를 로드하고 전처리하는 함수"""
    print("재고 데이터 로드 및 전처리 시작...")
    
    # 데이터 로드 및 정리
    df_raw = pd.read_excel("재고리스트_현기.xlsx", sheet_name=None)
    df_list = [df.assign(모델=sheet) for sheet, df in df_raw.items() if "조건" not in sheet]
    df = pd.concat(df_list, ignore_index=True)
    df = df.dropna(subset=["가격"])
    
    # 컬럼 정리
    if "모델" in df.columns:
        cols = df.columns.tolist()
        cols.insert(7, cols.pop(cols.index("모델")))
        df = df[cols]
    df = df.iloc[:, 1:13]
    df.columns = ["판매코드A", "판매코드B", "컬러코드A", "컬러코드B", "요청", "재고", "모델", "트림", "옵션", "외장컬러", "내장컬러", "가격"]
    
    print(f"✅ 전처리 완료! {len(df)}개 차량 데이터")
    return df

if __name__ == "__main__":
    # 테스트용 실행
    df = clean_data()
    print(f"처리된 데이터 샘플:")
    print(df.head()) 
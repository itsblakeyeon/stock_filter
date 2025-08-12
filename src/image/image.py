#!/usr/bin/env python3
import pandas as pd


def add_image_urls(df):
    """데이터프레임에 이미지 URL 컬럼을 추가하는 함수"""
    print("🖼️ 이미지 URL 추가 중...")
    
    # 이미지 URL 컬럼 초기화
    df["image_thumbnail"] = ""
    df["image_detail"] = ""
    
    # 브랜드별로 이미지 URL 생성
    for idx, row in df.iterrows():
        brand = row.get("company", "")
        model = row.get("model", "")
        trim = row.get("trim", "")
        
        # 기본 이미지 URL 생성
        thumbnail_url = generate_thumbnail_url(brand, model, trim)
        detail_url = generate_detail_url(brand, model, trim)
        
        df.at[idx, "image_thumbnail"] = thumbnail_url
        df.at[idx, "image_detail"] = detail_url
    
    print(f"✅ 이미지 URL 추가 완료: {len(df)}개 차량")
    return df


def generate_thumbnail_url(brand, model, trim):
    """썸네일 이미지 URL 생성"""
    if not brand or not model:
        return ""
    
    # 브랜드별 기본 URL 패턴
    if brand == "현대":
        base_url = "https://www.hyundai.com/kr/ko/e/vehicles"
    elif brand == "기아":
        base_url = "https://www.kia.com/kr/vehicles"
    else:
        return ""
    
    # 모델별 URL 생성
    model_url = f"{base_url}/{model.lower()}"
    
    return model_url


def generate_detail_url(brand, model, trim):
    """상세 이미지 URL 생성"""
    if not brand or not model:
        return ""
    
    # 브랜드별 기본 URL 패턴
    if brand == "현대":
        base_url = "https://www.hyundai.com/kr/ko/e/vehicles"
    elif brand == "기아":
        base_url = "https://www.kia.com/kr/vehicles"
    else:
        return ""
    
    # 모델별 URL 생성 (트림 정보 포함)
    if trim and trim != "?":
        model_url = f"{base_url}/{model.lower()}/{trim.lower()}"
    else:
        model_url = f"{base_url}/{model.lower()}"
    
    return model_url


def get_car_images(brand, model, trim=""):
    """특정 차량의 이미지 정보를 반환하는 함수"""
    thumbnail_url = generate_thumbnail_url(brand, model, trim)
    detail_url = generate_detail_url(brand, model, trim)
    
    return {
        "thumbnail": thumbnail_url,
        "detail": detail_url,
        "brand": brand,
        "model": model,
        "trim": trim
    }



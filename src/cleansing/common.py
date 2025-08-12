#!/usr/bin/env python3
"""
클렌징 공통 유틸리티 모듈
현대와 기아에서 공통으로 사용 가능한 안전한 함수들만 포함
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.config.constants import DataProcessing


def extract_year(raw_model: str) -> str:
    """
    모델명에서 연도 추출 (현대/기아 공통 로직)
    
    Args:
        raw_model: 원본 모델명
        
    Returns:
        추출된 연도 (기본값: "2025")
    """
    if not raw_model:
        return "2025"
        
    if "26" in raw_model:
        return "2026"
    elif "25" in raw_model:
        return "2025"
    else:
        return "2025"


def initialize_base_columns(df, company_name: str):
    """
    기본 컬럼 초기화 (현대/기아 공통)
    
    Args:
        df: 데이터프레임
        company_name: 회사명 ("현대" 또는 "기아")
    
    Returns:
        초기화된 데이터프레임
    """
    df["company"] = company_name
    df["model"] = ""
    df["trim"] = ""
    df["year"] = ""
    df["fuel"] = ""
    
    # options가 이미 존재하지 않을 때만 초기화
    if "options" not in df.columns:
        df["options"] = ""
    
    df["wheel_tire"] = ""
    
    # color 필드들이 이미 존재하지 않을 때만 초기화
    if "color_exterior" not in df.columns:
        df["color_exterior"] = ""
    if "color_interior" not in df.columns:
        df["color_interior"] = ""
    
    return df


def reorder_cleansing_columns(df):
    """
    클렌징 결과 컬럼 순서 정렬 (현대/기아 공통)
    
    Args:
        df: 데이터프레임
        
    Returns:
        컬럼 순서가 정렬된 데이터프레임
    """
    # 기본 컬럼 순서
    column_order = DataProcessing.BASE_COLUMNS.copy()
    
    # 현재 데이터프레임에 있는 컬럼들
    current_columns = list(df.columns)
    
    # 순서대로 있는 컬럼들
    ordered_columns = [col for col in column_order if col in current_columns]
    
    # 나머지 컬럼들
    remaining_columns = [col for col in current_columns if col not in ordered_columns]
    
    # 최종 순서
    final_order = ordered_columns + remaining_columns
    
    return df[final_order]


def basic_fuel_extraction(raw_text: str) -> str:
    """
    기본 연료 타입 추출 (현대/기아 공통 로직만)
    
    주의: 브랜드별 특수 연료 타입은 각 모듈에서 처리
    
    Args:
        raw_text: 원본 텍스트
        
    Returns:
        연료 타입
    """
    if not raw_text:
        return ""
        
    raw_text = raw_text.upper()
    
    # 공통으로 사용되는 기본 연료 타입만
    if "전기모터" in raw_text or "전기" in raw_text:
        return "전기"
    elif "하이브리드" in raw_text:
        return "하이브리드"
    else:
        return "가솔린"  # 기본값


def clean_text(text: str) -> str:
    """
    텍스트 정리 (공백, 특수문자 제거)
    
    Args:
        text: 정리할 텍스트
        
    Returns:
        정리된 텍스트
    """
    if not text or not isinstance(text, str):
        return ""
        
    # 앞뒤 공백 제거
    cleaned = text.strip()
    
    # 연속된 공백을 단일 공백으로 변경
    cleaned = " ".join(cleaned.split())
    
    return cleaned


def validate_dataframe(df, required_columns: list) -> bool:
    """
    데이터프레임 유효성 검사
    
    Args:
        df: 검사할 데이터프레임
        required_columns: 필수 컬럼 목록
        
    Returns:
        유효성 검사 결과
    """
    if df is None or df.empty:
        print("❌ 데이터프레임이 비어있습니다.")
        return False
        
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ 필수 컬럼이 누락되었습니다: {missing_columns}")
        return False
        
    print(f"✅ 데이터프레임 유효성 검사 통과: {len(df)}행, {len(df.columns)}개 컬럼")
    return True


def print_processing_status(step: str, count: int):
    """
    처리 상태 출력 (공통 포맷)
    
    Args:
        step: 처리 단계명
        count: 처리된 항목 수
    """
    print(f"✅ {step} 완료: {count}개")


def clean_options_text(options_text: str) -> str:
    """
    옵션 텍스트 정리
    
    Args:
        options_text: 원본 옵션 텍스트
        
    Returns:
        정리된 옵션 텍스트
    """
    if not options_text or not isinstance(options_text, str):
        return ""
    
    # 기본 텍스트 정리
    cleaned = clean_text(options_text)
    
    # 불필요한 기호 제거
    cleaned = cleaned.replace("【", "").replace("】", "")
    cleaned = cleaned.replace("｜", "|").replace("／", "/")
    
    return cleaned
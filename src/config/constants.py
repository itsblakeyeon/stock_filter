#!/usr/bin/env python3
"""
통합 상수 모듈
프로젝트 전체에서 사용되는 상수들을 중앙 관리
"""
from datetime import datetime

# 전역 날짜 설정 (기본값: None = 오늘 날짜 사용)
_GLOBAL_DATE = None

def set_global_date(date_str):
    """전역 날짜를 설정 (YYMMDD 형식)"""
    global _GLOBAL_DATE
    _GLOBAL_DATE = date_str

def get_today_date_string():
    """설정된 날짜 또는 오늘 날짜를 YYMMDD 형식으로 반환"""
    if _GLOBAL_DATE:
        return _GLOBAL_DATE
    return datetime.now().strftime("%y%m%d")

def get_raw_file_path(company, date_str=None):
    """날짜가 포함된 raw 파일 경로를 생성"""
    if date_str is None:
        date_str = get_today_date_string()
    
    if company.lower() == "hyundai":
        return f"data/raw/재고리스트_현대_{date_str}.xlsx"
    elif company.lower() == "kia":
        return f"data/raw/재고리스트_기아_{date_str}.xls"
    else:
        raise ValueError(f"Unknown company: {company}")

# 파일 경로 설정
class FilePaths:
    # Raw data files (동적 생성을 위한 함수들)
    @staticmethod
    def get_hyundai_raw_file(date_str=None):
        return get_raw_file_path("hyundai", date_str)
    
    @staticmethod 
    def get_kia_raw_file(date_str=None):
        return get_raw_file_path("kia", date_str)
    
    # 기존 호환성을 위한 속성들 (오늘 날짜 기본값)
    @property
    def HYUNDAI_RAW_FILE(self):
        return self.get_hyundai_raw_file()
    
    @property
    def KIA_RAW_FILE(self):
        return self.get_kia_raw_file()
    
    # Results paths (최종 결과 파일용)
    RESULTS_DIR = "results"
    
    @staticmethod
    def get_results_file(file_type, date_str=None):
        """결과 파일 경로를 생성"""
        if date_str is None:
            date_str = get_today_date_string()

        import os
        results_dir = FilePaths.RESULTS_DIR
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        if file_type == "filtered":
            return os.path.join(results_dir, f"stock_filtered_{date_str}.xlsx")
        else:
            raise ValueError(f"Unknown file_type: {file_type}")


# 공통 컬럼 순서 (run.py에서 사용)
FINAL_COLUMN_ORDER = [
    "code_sales_a", "code_sales_b", "code_color_a", "code_color_b",
    "request", "stock", "company", "model_raw", "trim_raw",
    "model", "trim", "year", "options",
    "fuel", "wheel_tire", "color_exterior", "color_interior",
    "price", "key_admin"
]


# 데이터 처리 관련 상수
class DataProcessing:
    # 재고 필터링 임계값
    STOCK_THRESHOLD = 5

    # 기본 컬럼들
    BASE_COLUMNS = [
        "code_sales_a", "code_sales_b", "code_color_a", "code_color_b",
        "request", "stock", "company", "model_raw", "trim_raw",
        "model", "trim", "year", "options",
        "fuel", "wheel_tire", "color_exterior", "color_interior",
        "price", "key_admin"
    ]
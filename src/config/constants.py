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
    
    # Export paths (중간 처리 파일용, 사용 안함)
    EXPORT_DIR = "data/export"
    CLEANSING_HYUNDAI = "data/export/cleansing_hyundai.xlsx"
    CLEANSING_KIA = "data/export/cleansing_kia.xlsx" 
    CLEANSING_UNIFIED = "data/export/cleansing_stock_unified.xlsx"
    LISTING_UNIFIED = "data/export/stock_unified.xlsx"
    
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
            
        if file_type == "all":
            return os.path.join(results_dir, f"stock_all_{date_str}.xlsx")
        elif file_type == "selected":
            return os.path.join(results_dir, f"stock_selected_{date_str}.xlsx")
        elif file_type == "upload":
            return os.path.join(results_dir, f"stock_upload_{date_str}.xlsx")
        else:
            raise ValueError(f"Unknown file_type: {file_type}")
    
    # Reference data
    PRICE_REFERENCE = "data/reference/price_reference.xlsx"


# 가격 계산 관련 상수
class PricingConfig:
    # 금융 파라미터
    INTEREST_RATE = 0.11
    DEPRECIATION_RATE_5_YEARS = 0.13
    DEPRECIATION_RATE_6_YEARS = 0.12
    DOWN_PAYMENT_RATE = 0.20
    
    # 대손 계수
    RETURN_TYPE_LOSS = 1.02
    PURCHASE_TYPE_LOSS = 1.02
    
    # 기본값
    DEFAULT_CAR_PRICE = 39510000.0
    REGISTRATION_FEE = 200000
    
    # 케어 비용
    CARE_FEE_ELECTRIC = 40000
    CARE_FEE_OTHER = 0
    
    # 전기차 세금 보조금
    ELECTRIC_TAX_SUBSIDY = 1400000


# 옵션 프라이싱 설정
class OptionConfig:
    PREMIUM_RATE = 0.50  # 50%


# 연도별 정보 (중복 제거용)
YEAR_INFO = {
    "Y0": {"term": 0, "discount": 1.00, "troi": {"반납형": None, "인수형": None}},
    "Y1": {"term": 12, "discount": 0.94, "troi": {"반납형": 6, "인수형": 12}},
    "Y2": {"term": 24, "discount": 0.89, "troi": {"반납형": 6, "인수형": 12}},
    "Y3": {"term": 36, "discount": 0.84, "troi": {"반납형": 6, "인수형": 12}},
    "Y4": {"term": 48, "discount": 0.79, "troi": {"반납형": 6, "인수형": 12}},
    "Y5": {"term": 60, "discount": 0.75, "troi": {"반납형": 6, "인수형": 12}},
    "Y6": {"term": 72, "discount": 0.71, "troi": {"반납형": 6, "인수형": 12}},
    "Y7": {"term": 84, "discount": 0.67, "troi": {"반납형": 6, "인수형": 12}},
}


# 구독료 계산에 사용되는 기간들
SUBSCRIPTION_TERMS = [12, 36, 60, 84]


# 비용 구조 상수
class CostStructure:
    # 초기 비용
    INITIAL_COSTS = {
        "adv": 1500000,
        "blackbox": 50000,
        "tint_highpass": 60000,
        "delivery": 200000,
        "misc": 10000,
    }
    
    # 연간 반복 비용
    RECURRING_YEARLY_COSTS = {
        "labor": 600000,
        "car_tax": 720000,
        "monitoring": 132000,
    }


# 공통 컬럼 순서 (run.py에서 사용)
FINAL_COLUMN_ORDER = [
    "code_sales_a",
    "code_sales_b", 
    "code_color_a",
    "code_color_b",
    "request",
    "stock",
    "image_thumbnail",
    "image_detail",
    "model_raw",
    "trim_raw",
    "key_admin",
    "key_subsidy",
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
    "price_car_original",
    "price_car_tax_pre",
    "price_car_tax_post",
    "price_options",
    "price_tax",
    "price_registration",
    "rebate",
    "promotion",
    "subsidy_national",
    "subsidy_lease",
    "subsidy_tax",
    "fee_list",
    "fee_care",
    "fee_return_12m",
    "fee_return_36m",
    "fee_return_60m",
    "fee_return_84m",
    "fee_purchase_12m",
    "fee_purchase_36m",
    "fee_purchase_60m",
    "fee_purchase_84m",
    "fee_options_12m",
    "fee_options_36m",
    "fee_options_60m",
    "fee_options_84m",
    "fee_return_options_12m",
    "fee_return_options_36m",
    "fee_return_options_60m",
    "fee_return_options_84m",
    "fee_purchase_options_12m",
    "fee_purchase_options_36m",
    "fee_purchase_options_60m",
    "fee_purchase_options_84m",
]


# 데이터 처리 관련 상수
class DataProcessing:
    # 재고 필터링 임계값
    STOCK_THRESHOLD = 5
    
    # 기본 컬럼들
    BASE_COLUMNS = [
        "code_sales_a", "code_sales_b", "code_color_a", "code_color_b",
        "request", "stock", "company", "model_raw", "trim_raw", "key_subsidy",
        "model", "trim", "year", "fuel", "options", "wheel_tire", 
        "color_exterior", "color_interior", "price_car_original"
    ]
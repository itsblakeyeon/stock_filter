# Stock Filter Project

재고 필터링 프로젝트 - 현대/기아 차량 재고 데이터 필터링

## 🚀 빠른 시작

### 첫 번째 설정 (새 맥에서)
```bash
# 1. 프로젝트 클론 또는 다운로드
git clone <repository-url>
cd stock_filter

# 2. 가상환경 생성
python3 -m venv venv

# 3. 가상환경 활성화
source venv/bin/activate

# 4. 의존성 설치
pip install -r requirements.txt
```

### 맥을 번갈아 사용할 때
```bash
# 1. 프로젝트 폴더로 이동
cd /path/to/stock_filter

# 2. 기존 가상환경 삭제 후 새로 생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📁 프로젝트 구조
```
stock_filter/
├── venv/                    # 가상환경 (Git에서 제외됨)
├── src/                     # 소스 코드
│   ├── cleansing/           # 데이터 클렌징 모듈
│   │   ├── cleansing_hyundai.py
│   │   ├── cleansing_kia.py
│   │   ├── cleansing_unified.py
│   │   └── common.py
│   ├── listing/             # 리스팅 필터링 모듈
│   │   └── listing_unified.py
│   └── config/              # 설정 모듈
│       └── constants.py
├── data/                    # 데이터 파일
│   └── raw/                 # 원본 데이터
│       ├── 재고리스트_현대_YYMMDD.xlsx
│       └── 재고리스트_기아_YYMMDD.xls
├── results/                 # 결과 파일
│   └── stock_filtered_YYMMDD.xlsx
├── run.py                   # 메인 실행 스크립트
├── requirements.txt         # Python 의존성
└── README.md               # 이 파일
```

## 🛠️ 사용법

### 가상환경 활성화
```bash
source venv/bin/activate
```

### 실행
```bash
# 메인 스크립트 실행 (날짜 입력 → 클렌징 → 필터링)
python run.py
```

### 개별 모듈 실행
```bash
# 클렌징만
python -m src.cleansing.cleansing_hyundai
python -m src.cleansing.cleansing_kia
python -m src.cleansing.cleansing_unified

# 리스팅만
python -m src.listing.listing_unified
```

## 📊 주요 기능

### 데이터 클렌징 (`src/cleansing/`)
- **cleansing_hyundai.py**: 현대차 재고 데이터 전처리
- **cleansing_kia.py**: 기아차 재고 데이터 전처리
- **cleansing_unified.py**: 두 브랜드 데이터 통합
- **common.py**: 공통 유틸리티 함수

### 리스팅 필터링 (`src/listing/`)
- **listing_unified.py**: 필터링 로직
  - 기본 휠&타이어만 (제네시스 18인치 포함)
  - 빌트인캠 또는 무옵션 차량만
  - 싼타페 하이브리드 5인승만
  - 팰리세이드 9인승만

### 설정 (`src/config/`)
- **constants.py**: 프로젝트 전역 상수 및 설정

## 🚀 실행 흐름

### run.py
1. 날짜 입력 받기 (YYMMDD 형식)
2. 해당 날짜의 재고 파일 확인
3. 클렌징 실행 (현대차 + 기아차 통합)
4. 리스팅 필터링 실행
5. 결과 파일 생성 (`results/stock_filtered_YYMMDD.xlsx`)

## ⚠️ 주의사항

- **가상환경**: `venv` 폴더는 Git에서 제외되므로 각 맥에서 새로 생성해야 합니다
- **데이터 파일**: `data/raw/` 폴더의 Excel 파일들은 날짜별로 관리됩니다
  - 형식: `재고리스트_현대_YYMMDD.xlsx`, `재고리스트_기아_YYMMDD.xls`
- **결과 파일**: 모든 결과 파일은 `results/` 폴더에 날짜별로 저장됩니다

## 🔧 개발 환경

- Python 3.9+
- pandas, openpyxl, xlrd, requests (requirements.txt 참조)
- macOS 권장

## 📝 개발자 노트

### 프로젝트 특징
- **간결함**: Cleansing → Listing 2단계 파이프라인
- **모듈화**: 기능별로 분리되어 유지보수가 용이
- **확장성**: 새로운 필터링 조건 추가 용이

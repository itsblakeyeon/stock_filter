# Stock Management Project

재고 관리 및 가격 분석 프로젝트

## 🚀 빠른 시작

### 첫 번째 설정 (새 맥에서)
```bash
# 1. 프로젝트 클론 또는 다운로드
git clone <repository-url>
cd Stock

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
cd /path/to/Stock

# 2. 기존 가상환경 삭제 후 새로 생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📁 프로젝트 구조
```
Stock/
├── venv/                    # 가상환경 (Git에서 제외됨)
├── src/                     # 소스 코드
│   ├── cleansing/           # 데이터 클렌징 모듈
│   │   ├── cleansing_hyundai.py
│   │   ├── cleansing_kia.py
│   │   └── cleansing_unified.py
│   ├── pricing/             # 가격 계산 모듈
│   │   ├── pricing.py
│   │   └── subsidy.py
│   ├── listing/             # 리스팅 모듈
│   │   ├── listing.py
│   │   └── listing_unified.py
│   ├── image/               # 이미지 관리 모듈
│   │   ├── image.py
│   │   └── image_crawler.py
│   └── utils/               # 유틸리티 모듈
│       └── export_cleansing_results.py
├── data/                    # 데이터 파일
│   ├── raw/                 # 원본 데이터
│   │   ├── 재고리스트_현대.xlsx
│   │   └── 재고리스트_기아.xls
│   ├── reference/           # 참조 데이터
│   │   └── price_reference.xlsx # 통합 가격 참조
│   └── export/              # 내보내기 결과
│       ├── stock_*.xlsx     # 리스팅 결과
│       └── cleansing_*.xlsx # 클렌징 결과
├── run_cleansing.py         # 클렌징 실행 스크립트
├── run_listing.py           # 리스팅 실행 스크립트
├── run_export.py            # 내보내기 실행 스크립트
├── requirements.txt         # Python 의존성
└── README.md               # 이 파일
```

## 🛠️ 사용법

### 가상환경 활성화
```bash
source venv/bin/activate
```

### 1. 클렌징 실행
```bash
# 모든 클렌징 실행
python run_cleansing.py

# 또는 개별 실행
python -m src.cleansing.cleansing_hyundai
python -m src.cleansing.cleansing_kia
python -m src.cleansing.cleansing_unified
```

### 2. 리스팅 실행
```bash
# 대화형 리스팅 실행
python run_listing.py

# 또는 개별 실행
python -m src.listing.listing
python -m src.listing.listing_unified
```

### 3. 내보내기 실행
```bash
# 클렌징 결과를 엑셀로 내보내기
python run_export.py

# 또는 직접 실행
python -m src.utils.export_cleansing_results
```



### 5. 이미지 관리
```bash
# 이미지 URL 생성 테스트
python -m src.image.image

# 이미지 크롤링
python -m src.image.image_crawler
```

## 📊 주요 기능

### 데이터 클렌징 (`src/cleansing/`)
- **cleansing_hyundai.py**: 현대차 재고 데이터 전처리
- **cleansing_kia.py**: 기아차 재고 데이터 전처리
- **cleansing_unified.py**: 두 브랜드 데이터 통합

### 가격 계산 (`src/pricing/`)
- **pricing.py**: 차량 가격, 취득세, 보조금 등 종합 비용 계산
- **price_reference.py**: 통합 가격 참조 데이터 로드 및 검색 (보조금 + 가격)

### 리스팅 (`src/listing/`)
- **listing.py**: 현대차 리스팅 생성
- **listing_unified.py**: 통합 리스팅 생성

### 이미지 관리 (`src/image/`)
- **image.py**: 차량 이미지 URL 생성 및 관리
- **image_crawler.py**: 차량 이미지 크롤링 및 다운로드

### 유틸리티 (`src/utils/`)
- **export_cleansing_results.py**: 클렌징 결과를 엑셀로 저장
- **create_price_reference.py**: 통합 가격 참조 파일 생성

## 🚀 실행 스크립트

### run_cleansing.py
- 현대차, 기아차, 통합 클렌징을 순차적으로 실행
- 각 단계별 결과를 콘솔에 출력

### run_listing.py
- 대화형으로 리스팅 종류 선택 가능
- 현대차 리스팅, 통합 리스팅, 또는 둘 다 실행

### run_export.py
- 클렌징 결과를 엑셀 파일로 저장
- 현대차, 기아차, 통합 결과를 각각 저장



## ⚠️ 주의사항

- **가상환경**: `venv` 폴더는 Git에서 제외되므로 각 맥에서 새로 생성해야 합니다
- **데이터 파일**: `data/raw/` 폴더의 Excel 파일들은 Git에 포함되지 않으므로 별도로 관리하세요
- **의존성**: `requirements.txt`에 명시된 패키지들이 필요합니다
- **경로**: 데이터 파일 경로가 `data/raw/`로 변경되었습니다
- **결과 파일**: 모든 결과 파일은 `data/export/` 폴더에 저장됩니다
- **참조 파일**: 가격 및 보조금 참조 데이터는 `data/reference/` 폴더에 저장됩니다

## 🔧 개발 환경

- Python 3.8+
- pandas, openpyxl, numpy 등 (requirements.txt 참조)
- macOS 권장

## 📝 개발자 노트

### 폴더 구조의 장점
- **모듈화**: 기능별로 분리되어 유지보수가 용이
- **확장성**: 새로운 기능 추가 시 적절한 폴더에 배치
- **가독성**: 파일 구조만 봐도 프로젝트 구조 파악 가능
- **재사용성**: 각 모듈을 독립적으로 import하여 사용 가능

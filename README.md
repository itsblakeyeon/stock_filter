# Stock Management Project

재고 관리 및 가격 분석 프로젝트

## 🚀 빠른 시작

### 첫 번째 설정 (새 맥에서)
```bash
# 1. 프로젝트 클론 또는 다운로드
git clone <repository-url>
cd Stock

# 2. 자동 설정 스크립트 실행
./setup.sh
```

### 수동 설정
```bash
# 1. 가상환경 생성
python3 -m venv venv

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt
```

## 🔄 맥을 번갈아 사용할 때

### 새 맥에서 작업 시작
```bash
# 1. 프로젝트 폴더로 이동
cd /path/to/Stock

# 2. 자동 설정 (기존 venv 삭제 후 새로 생성)
./setup.sh

# 또는 수동으로:
rm -rf venv  # 기존 가상환경 삭제
python3 -m venv venv  # 새 가상환경 생성
source venv/bin/activate
pip install -r requirements.txt
```

### 작업 완료 후
```bash
# 변경사항 커밋
git add .
git commit -m "작업 내용 설명"
git push  # 원격 저장소가 있는 경우
```

## 📁 프로젝트 구조
```
Stock/
├── venv/              # 가상환경 (Git에서 제외됨)
├── *.py              # Python 스크립트
├── *.xlsx            # Excel 데이터 파일
├── requirements.txt  # Python 의존성
├── setup.sh         # 자동 설정 스크립트
└── README.md        # 이 파일
```

## ⚠️ 주의사항

- **가상환경 중복 방지**: `venv` 폴더는 Git에서 제외되므로 각 맥에서 새로 생성해야 합니다
- **데이터 파일**: Excel 파일들은 Git에 포함되지 않으므로 별도로 관리하세요
- **설정 스크립트**: `./setup.sh`를 사용하면 자동으로 올바른 환경을 설정할 수 있습니다

## 🛠️ 사용법

```bash
# 가상환경 활성화
source venv/bin/activate

# 데이터 정리
python cleansing.py

# 가격 분석
python pricing.py

# 리스트 생성
python listing.py
```

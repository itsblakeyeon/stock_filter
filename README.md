# Stock Calculator

차량 재고 데이터 처리 및 구독료 계산 도구

## 사용법

```bash
python stock_calculator.py
```

## 파일 구조

- `stock_calculator.py`: 메인 스크립트 (모든 기능 통합)
- `재고리스트_현기.xlsx`: 원본 데이터
- `stock_result.xlsx`: 결과 파일 (28개 구독료 컬럼 포함)

## 구독료 옵션

- **반납형**: 12개월~84개월
- **인수형**: 12개월~84개월
- **반납형\_케어**: 기본 + 5만원/월
- **인수형\_케어**: 기본 + 5만원/월

## 가상환경 설정

```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas openpyxl
```

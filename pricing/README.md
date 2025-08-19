# Pricing 모듈

차량 프라이싱 계산을 위한 핵심 엔진입니다. Stock 프로젝트와 다른 애플리케이션에서 공통으로 사용할 수 있도록 설계되었습니다.

## 📁 구조

```
Pricing/
├── core/                    # 핵심 로직
│   ├── constants.py         # 상수 정의
│   ├── models.py           # 데이터 모델
│   ├── calculations.py     # 계산 함수들
│   └── __init__.py
├── calculator.py           # 사용하기 쉬운 인터페이스
├── example_usage.py        # 사용 예시
├── requirements.txt        # 의존성
└── README.md              # 이 파일
```

## 🚀 빠른 시작

### 기본 사용법

```python
from Pricing.calculator import quick_calculate

# 간단한 계산
result = quick_calculate(
    car_price=50000000,    # 5천만원
    fuel_type="전기",
    subsidy_national=80,   # 800만원 보조금
    company="현대"
)

print(f"36개월 반납형: {result['36개월_반납형']:,}원")
```

### 상세 계산

```python
from Pricing.calculator import calculate_pricing, print_pricing_result

result = calculate_pricing(
    car_price=55000000,      # 차량 가격
    option_price=3000000,    # 옵션 가격
    fuel_type="전기",        # 연료 타입
    subsidy_national=80,     # 국비 보조금 (만원)
    subsidy_lease=20,        # 리스 보조금 (만원)
    company="현대"           # 제조사
)

print_pricing_result(result)
```

### Core API 직접 사용

```python
from Pricing import calculate_pricing_complete

result = calculate_pricing_complete(
    car_price=48000000,
    option_price=1800000,
    fuel_type="전기",
    subsidy_national=80,
    company="현대"
)

print(f"총 차량 비용: {result.total_car_cost:,}원")
```

## 🔧 주요 기능

### 1. 차량 비용 계산
- 차량 가격 + 세금(7%)
- 각종 보조금 (국비, 리스, 전기차 세금 보조금)
- 리베이트 (테슬라 제외)
- 등록비

### 2. 구독료 계산
- **반납형**: 12, 36, 60, 84개월
- **인수형**: 12, 36, 60, 84개월
- 잔존가치 및 할인율 적용

### 3. 옵션 프라이싱
- 옵션 가격에 50% 프리미엄 적용
- 기간별 분할 계산

### 4. 통합 계산
- 차량 + 옵션 통합 구독료
- 케어 비용 (전기차 40,000원/월)

## 📊 계산 예시

### 아이오닉 6 (전기차)
```
차량가격: 52,000,000원
옵션가격: 2,500,000원
국비보조금: 800만원
```

**결과:**
- 총 차량비용: 46,040,000원
- 36개월 반납형: 1,285,000원/월
- 36개월 반납형(옵션포함): 1,389,000원/월

## 🔄 Stock 프로젝트와의 연동

Stock 프로젝트는 이 Pricing 모듈을 참조하도록 리팩토링되었습니다:

```python
# Stock/src/pricing/pricing.py에서
from Pricing import calculate_pricing_complete, SubscriptionInput

# 기존 함수들이 Pricing 엔진을 사용
def calculate_subscription_fees(car_price, fuel_type, subsidy_trim, company):
    subscription_input = SubscriptionInput(...)
    return pricing_calculate_subscription_fees(subscription_input)
```

## 🧪 테스트 실행

```bash
# 예시 실행
python example_usage.py

# 계산기 테스트
python calculator.py
```

## 📝 주요 상수

```python
# 금융 파라미터
INTEREST_RATE = 0.11                    # 금리 11%
DEPRECIATION_RATE_5_YEARS = 0.13        # 5년 감가상각률
DOWN_PAYMENT_RATE = 0.20                # 계약금 비율 20%

# 보조금
ELECTRIC_TAX_SUBSIDY = 1400000          # 전기차 세금 보조금

# 케어 비용
CARE_FEE_ELECTRIC = 40000               # 전기차 케어비 월 4만원
CARE_FEE_OTHER = 0                      # 기타 차량 케어비 없음
```

## 🔧 확장 가능성

이 모듈은 다음과 같이 확장 가능합니다:

1. **웹 애플리케이션**: Flask/Django/FastAPI 등과 연동
2. **Streamlit 앱**: 대화형 웹 인터페이스
3. **API 서버**: REST API 엔드포인트 제공
4. **CLI 도구**: 명령줄 인터페이스
5. **다른 프로젝트**: 모듈 import로 바로 사용

## 📋 TODO

- [ ] 단위 테스트 추가
- [ ] 타입 힌트 개선
- [ ] 설정 파일 지원
- [ ] 로깅 추가
- [ ] 성능 최적화
#!/usr/bin/env python3
"""
차량 프라이싱 계산기
사용하기 쉬운 계산기 인터페이스 제공
"""

from core import calculate_pricing_complete, get_subsidy_info, get_price_info


def calculate_pricing(
    car_price,
    option_price=0,
    fuel_type="",
    subsidy_national=0,
    subsidy_lease=0,
    company="",
    terms=None
):
    """
    차량 프라이싱 계산 (간단한 인터페이스)
    
    Args:
        car_price (float): 차량 가격 (원)
        option_price (float): 옵션 가격 (원)
        fuel_type (str): 연료 타입 ("전기", "가솔린", "디젤" 등)
        subsidy_national (float): 국비 보조금 (만원 단위)
        subsidy_lease (float): 리스 보조금 (만원 단위)
        company (str): 제조사 ("테슬라" 제외시 리베이트 적용)
        terms (list): 계산할 기간 리스트 (기본: [12, 36, 60, 84])
    
    Returns:
        dict: 프라이싱 계산 결과
    
    Example:
        >>> result = calculate_pricing(
        ...     car_price=50000000,
        ...     option_price=2000000,
        ...     fuel_type="전기",
        ...     subsidy_national=80,
        ...     company="현대"
        ... )
        >>> print(f"12개월 반납형: {result['fees']['fee_return_options_12m']:,}원")
    """
    if terms is None:
        terms = [12, 36, 60, 84]
    
    result = calculate_pricing_complete(
        car_price=car_price,
        option_price=option_price,
        fuel_type=fuel_type,
        subsidy_national=subsidy_national,
        subsidy_lease=subsidy_lease,
        company=company,
        terms=terms
    )
    
    # 사용하기 쉬운 형태로 재구성
    formatted_result = {
        "input": {
            "차량가격": f"{car_price:,}원",
            "옵션가격": f"{option_price:,}원",
            "연료타입": fuel_type,
            "국비보조금": f"{subsidy_national}만원",
            "리스보조금": f"{subsidy_lease}만원",
            "제조사": company,
        },
        "cost_breakdown": {
            "차량가격": result.car_cost_detail.car,
            "세금(7%)": result.car_cost_detail.tax,
            "국비보조금": result.car_cost_detail.subsidy_national,
            "리스보조금": result.car_cost_detail.subsidy_lease,
            "전기차세금보조금": result.car_cost_detail.subsidy_tax,
            "리베이트": result.car_cost_detail.rebate,
            "등록비": result.car_cost_detail.plate,
            "총차량비용": result.total_car_cost,
        },
        "fees": {
            **result.subscription_fees,
            **result.option_fees,
            **result.combined_fees,
            "케어비용": result.care_fee,
        },
        "summary": result.summary
    }
    
    return formatted_result


def print_pricing_result(result):
    """
    프라이싱 결과를 보기 좋게 출력
    
    Args:
        result: calculate_pricing()의 결과
    """
    print("\n" + "="*60)
    print("🚗 차량 프라이싱 계산 결과")
    print("="*60)
    
    # 입력 정보
    print("\n📝 입력 정보:")
    for key, value in result["input"].items():
        print(f"  {key}: {value}")
    
    # 비용 상세
    print("\n💰 비용 상세:")
    cost = result["cost_breakdown"]
    print(f"  차량가격:        {cost['차량가격']:>12,}원")
    print(f"  세금(7%):        {cost['세금(7%)']:>12,}원")
    if cost['국비보조금'] != 0:
        print(f"  국비보조금:      {cost['국비보조금']:>12,}원")
    if cost['리스보조금'] != 0:
        print(f"  리스보조금:      {cost['리스보조금']:>12,}원")
    if cost['전기차세금보조금'] != 0:
        print(f"  전기차세금보조금: {cost['전기차세금보조금']:>12,}원")
    if cost['리베이트'] != 0:
        print(f"  리베이트:        {cost['리베이트']:>12,}원")
    print(f"  등록비:          {cost['등록비']:>12,}원")
    print("  " + "-"*30)
    print(f"  총 차량비용:     {cost['총차량비용']:>12,}원")
    
    # 구독료 (반납형)
    print("\n🔄 반납형 구독료:")
    fees = result["fees"]
    for term in [12, 36, 60, 84]:
        base_key = f"fee_return_{term}m"
        option_key = f"fee_return_options_{term}m"
        
        if base_key in fees:
            base_fee = fees[base_key]
            option_fee = fees.get(option_key, base_fee)
            print(f"  {term:2d}개월: {base_fee:>10,}원 (옵션포함: {option_fee:>10,}원)")
    
    # 구독료 (인수형)
    print("\n💰 인수형 구독료:")
    for term in [12, 36, 60, 84]:
        base_key = f"fee_purchase_{term}m"
        option_key = f"fee_purchase_options_{term}m"
        
        if base_key in fees:
            base_fee = fees[base_key]
            option_fee = fees.get(option_key, base_fee)
            print(f"  {term:2d}개월: {base_fee:>10,}원 (옵션포함: {option_fee:>10,}원)")
    
    # 기타 비용
    if fees.get("케어비용", 0) > 0:
        print(f"\n🔧 케어비용: {fees['케어비용']:,}원/월")
    
    print("\n" + "="*60)


def quick_calculate(car_price, fuel_type="", subsidy_national=0, company=""):
    """
    빠른 계산 (가장 기본적인 정보만으로)
    
    Args:
        car_price: 차량 가격
        fuel_type: 연료 타입 (기본: "")
        subsidy_national: 국비 보조금 만원 단위 (기본: 0)
        company: 제조사 (기본: "")
    
    Returns:
        dict: 주요 구독료 정보
    """
    result = calculate_pricing(
        car_price=car_price,
        fuel_type=fuel_type,
        subsidy_national=subsidy_national,
        company=company
    )
    
    fees = result["fees"]
    return {
        "총차량비용": result["cost_breakdown"]["총차량비용"],
        "12개월_반납형": fees.get("fee_return_12m", 0),
        "36개월_반납형": fees.get("fee_return_36m", 0),
        "60개월_반납형": fees.get("fee_return_60m", 0),
        "12개월_인수형": fees.get("fee_purchase_12m", 0),
        "36개월_인수형": fees.get("fee_purchase_36m", 0),
        "60개월_인수형": fees.get("fee_purchase_60m", 0),
    }


def calculate_with_reference(
    model="",
    trim="",
    year="",
    key_subsidy="",
    fuel_type="",
    company="",
    option_price=0,
    terms=None
):
    """
    참조 데이터를 활용한 자동 계산
    
    Args:
        model: 모델명 (예: "아이오닉6")
        trim: 트림명 (예: "프레스티지")
        year: 연식 (예: "2024")
        key_subsidy: 보조금 키 (예: "아이오닉6 프레스티지")
        fuel_type: 연료 타입 (예: "전기")
        company: 제조사 (예: "현대")
        option_price: 추가 옵션 가격 (기본: 0)
        terms: 계산할 기간 리스트 (기본: [12, 36, 60, 84])
    
    Returns:
        dict: 프라이싱 계산 결과
    """
    # 가격 정보 조회
    price_info = get_price_info(model, trim, year)
    car_price = price_info.get('price_car_original', 0)
    
    if car_price == 0:
        print(f"⚠️ 모델 '{model}' 트림 '{trim}'의 가격 정보를 찾을 수 없습니다.")
        print("⚠️ 수동으로 car_price를 입력해야 합니다.")
        return None
    
    # 보조금 정보 조회
    subsidy_info = get_subsidy_info(key_subsidy, fuel_type)
    subsidy_national = subsidy_info.get('subsidy_national', 0) / 10000  # 만원 단위로 변환
    subsidy_lease = subsidy_info.get('subsidy_lease', 0) / 10000
    
    print(f"📋 참조 데이터 조회 결과:")
    print(f"  차량가격: {car_price:,}원")
    print(f"  국비보조금: {subsidy_national}만원")
    print(f"  리스보조금: {subsidy_lease}만원")
    print()
    
    # 일반 계산 함수 호출
    return calculate_pricing(
        car_price=car_price,
        option_price=option_price,
        fuel_type=fuel_type,
        subsidy_national=subsidy_national,
        subsidy_lease=subsidy_lease,
        company=company,
        terms=terms
    )


if __name__ == "__main__":
    # 사용 예시
    print("차량 프라이싱 계산기 예시")
    
    # 예시 1: 전기차
    print("\n예시 1: 전기차 (아이오닉 6)")
    result1 = calculate_pricing(
        car_price=50000000,      # 5천만원
        option_price=2000000,    # 200만원 옵션
        fuel_type="전기",
        subsidy_national=80,     # 800만원 보조금
        company="현대"
    )
    print_pricing_result(result1)
    
    # 예시 2: 가솔린차
    print("\n예시 2: 가솔린차 (그랜저)")
    result2 = quick_calculate(
        car_price=45000000,      # 4천5백만원
        company="현대"
    )
    print("주요 구독료:")
    for key, value in result2.items():
        print(f"  {key}: {value:,}원")
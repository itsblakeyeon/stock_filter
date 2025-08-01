#!/bin/bash

echo "🚀 Stock 프로젝트 설정 시작..."

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되어 있지 않습니다."
    exit 1
fi

echo "✅ Python3 확인됨: $(python3 --version)"

# 기존 가상환경 확인 및 삭제
if [ -d "venv" ]; then
    echo "⚠️  기존 가상환경 발견. 삭제 중..."
    rm -rf venv
fi

# 새 가상환경 생성
echo "📦 새 가상환경 생성 중..."
python3 -m venv venv

# 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# pip 업그레이드
echo "⬆️  pip 업그레이드 중..."
pip install --upgrade pip

# 의존성 설치
echo "📚 패키지 설치 중..."
pip install -r requirements.txt

echo "✅ 설정 완료!"
echo ""
echo "다음 명령어로 가상환경을 활성화하세요:"
echo "source venv/bin/activate"
echo ""
echo "프로젝트 실행:"
echo "python cleansing.py" 
#!/bin/bash
# MG Discovery Core - Dashboard Startup Script (Linux/Mac)

set -e

# 색상 설정
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리로 이동 (스크립트 위치 기준)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║        MG Discovery Core - Dashboard         ║"
echo "║          AlphaFold Drug Platform             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# 가상환경 확인
if [ ! -f ".venv/bin/activate" ]; then
    echo -e "${RED}[ERROR] .venv 가상환경이 없습니다.${NC}"
    echo "        다음 명령으로 생성하세요:"
    echo "          uv venv .venv"
    echo "          uv pip install -r requirements.txt"
    exit 1
fi

# 데이터베이스 존재 여부 확인
if [ ! -f "data/mg_discovery.db" ]; then
    echo -e "${YELLOW}[WARNING] data/mg_discovery.db 가 없습니다.${NC}"
    echo "          파이프라인을 먼저 실행하세요: ./run_pipeline.sh"
    echo ""
fi

# vina 실행 파일 확인 (OS별)
OS_TYPE=$(uname -s)
if [ "$OS_TYPE" = "Linux" ]; then
    if [ ! -f "vina_bin/linux/vina" ]; then
        echo -e "${YELLOW}[WARNING] vina_bin/linux/vina 가 없습니다.${NC}"
        echo "          README.md 의 Vina 설치 안내를 확인하세요."
    fi
elif [ "$OS_TYPE" = "Darwin" ]; then
    if [ ! -f "vina_bin/mac/vina" ]; then
        echo -e "${YELLOW}[WARNING] vina_bin/mac/vina 가 없습니다.${NC}"
        echo "          README.md 의 Vina 설치 안내를 확인하세요."
    fi
fi

# 가상환경 활성화
echo -e "${GREEN}[INFO] 가상환경 활성화 중...${NC}"
source .venv/bin/activate

# Streamlit 앱 실행
echo -e "${GREEN}[INFO] 대시보드를 시작합니다. (Port: 8501)${NC}"
echo -e "${CYAN}[INFO] 브라우저에서 http://localhost:8501 으로 접속하세요.${NC}"
echo -e "${GREEN}[INFO] 종료: Ctrl+C${NC}"
echo ""

streamlit run web/app.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false

echo ""
echo -e "${GREEN}[INFO] 서비스가 종료되었습니다.${NC}"

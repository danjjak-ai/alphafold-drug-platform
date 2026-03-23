#!/bin/bash
# MG Discovery Core - Data Pipeline (Linux/Mac)

# 오류 즉시 중단
set -e

# 색상 설정
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# 프로젝트 루트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║     MG Discovery Core - Data Pipeline        ║"
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

# OS별 vina 확인
OS_TYPE=$(uname -s)
if [ "$OS_TYPE" = "Linux" ]; then
    VINA_PATH="vina_bin/linux/vina"
elif [ "$OS_TYPE" = "Darwin" ]; then
    VINA_PATH="vina_bin/mac/vina"
fi

if [ -n "$VINA_PATH" ] && [ ! -f "$VINA_PATH" ]; then
    echo -e "${YELLOW}[WARNING] $VINA_PATH 가 없습니다.${NC}"
    echo "          README.md 의 Vina 설치 안내를 확인하세요."
    echo "          도킹 시뮬레이션(Step 7)은 실패할 수 있습니다."
    echo ""
fi

# 파이프라인 안내
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 파이프라인 실행 순서"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " [1] DB 초기화"
echo " [2] 타겟 단백질 데이터 수집"
echo " [3] 약물 (ChEMBL) 데이터 수집"
echo " [4] 학습 데이터 수집"
echo " [5] 타겟 단백질 구조 전처리"
echo " [6] 리간드 구조 전처리"
echo " [7] 도킹 시뮬레이션 (시간 소요)"
echo " [8] 도킹 결과 분석"
echo " [9] 약물 활성 예측"
echo " [10] 베이스라인 모델 학습"
echo " [11] AI 모델 학습"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 실행 확인
read -r -p "전체 파이프라인을 실행하시겠습니까? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "[INFO] 취소되었습니다."
    exit 0
fi

# 질환명 입력 처리
DISEASE=""
if [ -n "$1" ]; then
    DISEASE="$1"
    echo -e "${CYAN}[INFO] 질환명 파라미터 감지: ${BOLD}$DISEASE${NC}"
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo " 특정 질환에 대한 타겟 및 약물 데이터를 수집할 수 있습니다."
    echo " (영문 질환명을 입력하거나, 건너뛰려면 Enter를 누르세요)"
    echo " 예: Alzheimer, Diabetes, Cancer"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    read -r -p "질환명 (English): " DISEASE
fi

# 가상환경 활성화
echo -e "${GREEN}[INFO] 가상환경 활성화 중...${NC}"
source .venv/bin/activate

# 공통 실행 함수
run_step() {
    local STEP_NUM=$1
    local STEP_DESC=$2
    local SCRIPT=$3
    shift 3
    local EXTRA_ARGS="$@"

    echo ""
    echo -e "${CYAN}[$STEP_NUM/11] $STEP_DESC${NC}"
    if [ -n "$EXTRA_ARGS" ]; then
        python "$SCRIPT" "$EXTRA_ARGS"
    else
        python "$SCRIPT"
    fi
    echo -e "${GREEN}[OK] Step $STEP_NUM 완료${NC}"
}

# ── 파이프라인 실행 ──────────────────────────────
run_step 1  "DB 초기화"                       scripts/init_db.py
run_step 2  "타겟 단백질 데이터 수집"          scripts/fetch_targets.py "$DISEASE"
run_step 3  "약물 (ChEMBL) 데이터 수집"       scripts/fetch_drugs.py   "$DISEASE"
run_step 4  "학습 데이터 수집"                 scripts/fetch_training_data.py
run_step 5  "타겟 단백질 구조 전처리"          scripts/prepare_targets.py
run_step 6  "리간드 구조 전처리"               scripts/prepare_ligands.py
run_step 7  "도킹 시뮬레이션 (수 시간 소요)"  scripts/run_docking.py
run_step 8  "도킹 결과 분석"                   scripts/post_docking_analysis.py
run_step 9  "약물 활성 예측"                   scripts/predict_activity.py
run_step 10 "베이스라인 모델 학습"             scripts/train_baseline_model.py
run_step 11 "AI 모델 학습"                     scripts/train_ai_model.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}${BOLD} [SUCCESS] 전체 파이프라인 완료!${NC}"
echo " 대시보드 실행: ./start_dashboard.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

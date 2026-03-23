@echo off
chcp 65001 > nul
title MG Discovery Core - Data Pipeline

echo.
echo ╔══════════════════════════════════════════════╗
echo ║     MG Discovery Core - Data Pipeline        ║
echo ║          AlphaFold Drug Platform             ║
echo ╚══════════════════════════════════════════════╝
echo.

:: 프로젝트 루트 디렉토리로 이동
cd /d "%~dp0"

:: 가상환경 확인
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] .venv 가상환경이 없습니다.
    echo         다음 명령으로 생성하세요: uv venv .venv
    echo         패키지 설치: uv pip install -r requirements.txt
    pause
    exit /b 1
)

:: 가상환경 활성화
echo [INFO] 가상환경 활성화 중...
call .venv\Scripts\activate.bat

:: 오류 발생 시 즉시 중단 함수
set STEP=0
set FAILED=0

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  파이프라인 실행 순서
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  [1] DB 초기화
echo  [2] 타겟 단백질 데이터 수집
echo  [3] 약물 (ChEMBL) 데이터 수집
echo  [4] 학습 데이터 수집
echo  [5] 타겟 단백질 구조 전처리
echo  [6] 리간드 구조 전처리
echo  [7] 도킹 시뮬레이션 (시간 소요)
echo  [8] 도킹 결과 분석
echo  [9] 약물 활성 예측
echo  [10] 베이스라인 모델 학습
echo  [11] AI 모델 학습
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

set /p DISEASE="Enter disease name in English (e.g., Alzheimer): "
if "%DISEASE%"=="" (
    echo [ERROR] Disease name cannot be empty.
    pause
    exit /b 1
)

set /p CONFIRM="전체 파이프라인을 실행하시겠습니까? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo [INFO] 취소되었습니다.
    pause
    exit /b 0
)

:: ── Step 1: DB 초기화 ─────────────────────────────
echo.
echo [1/11] DB 초기화 중...
python scripts/init_db.py
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 1 실패: init_db.py & goto :FAILED )
echo [OK] Step 1 완료

:: ── Step 2: 타겟 단백질 데이터 수집 ─────────────────
echo.
echo [2/11] 타겟 단백질 데이터 수집 중... (질환: %DISEASE%)
python scripts/fetch_targets.py "%DISEASE%"
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 2 실패: fetch_targets.py & goto :FAILED )
echo [OK] Step 2 완료

:: ── Step 3: 약물 데이터 수집 ─────────────────────────
echo.
echo [3/11] 약물 (ChEMBL) 데이터 수집 중... (질환: %DISEASE%)
python scripts/fetch_drugs.py "%DISEASE%"
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 3 실패: fetch_drugs.py & goto :FAILED )
echo [OK] Step 3 완료

:: ── Step 4: 학습 데이터 수집 ─────────────────────────
echo.
echo [4/11] 학습 데이터 수집 중...
python scripts/fetch_training_data.py
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 4 실패: fetch_training_data.py & goto :FAILED )
echo [OK] Step 4 완료

:: ── Step 5: 타겟 단백질 구조 전처리 ─────────────────
echo.
echo [5/11] 타겟 단백질 구조 전처리 중...
python scripts/prepare_targets.py
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 5 실패: prepare_targets.py & goto :FAILED )
echo [OK] Step 5 완료

:: ── Step 6: 리간드 구조 전처리 ───────────────────────
echo.
echo [6/11] 리간드 구조 전처리 중...
python scripts/prepare_ligands.py
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 6 실패: prepare_ligands.py & goto :FAILED )
echo [OK] Step 6 완료

:: ── Step 7: 도킹 시뮬레이션 ───────────────────────────
echo.
echo [7/11] 도킹 시뮬레이션 실행 중... (수 시간 소요될 수 있습니다)
python scripts/run_docking.py
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 7 실패: run_docking.py & goto :FAILED )
echo [OK] Step 7 완료

:: ── Step 8: 도킹 결과 분석 ────────────────────────────
echo.
echo [8/11] 도킹 결과 분석 중...
python scripts/post_docking_analysis.py
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 8 실패: post_docking_analysis.py & goto :FAILED )
echo [OK] Step 8 완료

:: ── Step 9: 약물 활성 예측 ────────────────────────────
echo.
echo [9/11] 약물 활성 예측 중...
python scripts/predict_activity.py
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 9 실패: predict_activity.py & goto :FAILED )
echo [OK] Step 9 완료

:: ── Step 10: 베이스라인 모델 학습 ─────────────────────
echo.
echo [10/11] 베이스라인 모델 학습 중...
python scripts/train_baseline_model.py
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 10 실패: train_baseline_model.py & goto :FAILED )
echo [OK] Step 10 완료

:: ── Step 11: AI 모델 학습 ──────────────────────────────
echo.
echo [11/11] AI 모델 학습 중...
python scripts/train_ai_model.py
if %ERRORLEVEL% neq 0 ( echo [ERROR] Step 11 실패: train_ai_model.py & goto :FAILED )
echo [OK] Step 11 완료

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  [SUCCESS] 전체 파이프라인 완료!
echo  대시보드 실행: start_dashboard.bat
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
exit /b 0

:FAILED
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  [FAILED] 파이프라인 실행 중 오류가 발생했습니다.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
exit /b 1

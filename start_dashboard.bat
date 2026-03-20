@echo off
chcp 65001 > nul
title MG Discovery Core - Dashboard

echo.
echo ╔══════════════════════════════════════════════╗
echo ║        MG Discovery Core - Dashboard         ║
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

:: 데이터베이스 존재 여부 확인
if not exist "data\mg_discovery.db" (
    echo [WARNING] data\mg_discovery.db 가 없습니다.
    echo           파이프라인을 먼저 실행하세요: run_pipeline.bat
    echo.
)

:: 가상환경 활성화
echo [INFO] 가상환경 활성화 중...
call .venv\Scripts\activate.bat

:: Streamlit 앱 실행
echo [INFO] 대시보드를 시작합니다. (Port: 8501)
echo [INFO] 브라우저에서 http://localhost:8501 으로 접속하세요.
echo [INFO] 종료: Ctrl+C
echo.

streamlit run web/app.py ^
    --server.port 8501 ^
    --server.address localhost ^
    --browser.gatherUsageStats false

echo.
echo [INFO] 서비스가 종료되었습니다.
pause

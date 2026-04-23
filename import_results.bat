@echo off
chcp 65001 > nul
title MG Discovery Core - Import Colab Results

echo.
echo ╔══════════════════════════════════════════════╗
echo ║    MG Discovery Core - Results Importer      ║
echo ╚══════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

if not exist "discovery_results.zip" (
    echo [ERROR] discovery_results.zip 파일이 현재 디렉토리에 없습니다.
    echo         Colab에서 다운로드한 파일을 프로젝트 최상위 폴더에 넣어주세요.
    pause
    exit /b 1
)

echo [INFO] Colab 결과 압축 해제 중...
powershell -command "Expand-Archive -Force -Path 'discovery_results.zip' -DestinationPath '.'"

if %ERRORLEVEL% neq 0 (
    echo [ERROR] 압축 해제 중 오류가 발생했습니다.
    pause
    exit /b 1
)

echo [SUCCESS] 결과 데이터 병합이 완료되었습니다!
echo.
echo 이제 start_dashboard.bat를 실행하여 대시보드를 확인하세요.
pause
exit /b 0

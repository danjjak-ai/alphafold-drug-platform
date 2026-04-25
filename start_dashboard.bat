@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0start_dashboard.ps1"
if %ERRORLEVEL% neq 0 pause

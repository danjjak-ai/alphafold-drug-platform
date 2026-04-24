@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0import_results.ps1"
if %ERRORLEVEL% neq 0 pause

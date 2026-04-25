# MG Discovery Core - Start Dashboard (PowerShell)
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Host.UI.RawUI.WindowTitle = "MG Discovery Core - Dashboard"

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "         MG Discovery Core - Dashboard" -ForegroundColor Cyan
Write-Host "           AlphaFold Drug Platform" -ForegroundColor Cyan
Write-Host "==================================================`n" -ForegroundColor Cyan

$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $currentDir

# 1. Port 8501 Check and Cleanup
$portProcess = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($portProcess) {
    Write-Host "[INFO] Port 8501 is already in use by PID $portProcess. Attempting to free it..." -ForegroundColor Yellow
    try {
        Stop-Process -Id $portProcess -Force
        Start-Sleep -Seconds 1
    } catch {
        Write-Host "[WARN] Could not stop process $portProcess. Please close it manually." -ForegroundColor Red
    }
}

# 2. Virtual Environment Check
if (-not (Test-Path ".venv\Scripts\activate.ps1")) {
    Write-Host "[ERROR] .venv virtual environment not found." -ForegroundColor Red
    Write-Host "        Please create it using: uv venv .venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit..."
    exit
}

# 3. Database Check
if (-not (Test-Path "data\mg_discovery.db")) {
    Write-Host "[WARNING] data\mg_discovery.db not found. Pipeline results may be missing.`n" -ForegroundColor Yellow
}

# 4. Run Streamlit
Write-Host "[INFO] Starting dashboard on http://localhost:8501..." -ForegroundColor Green
Write-Host "[INFO] Press Ctrl+C to stop.`n" -ForegroundColor Gray

# Activate environment and run
# Note: In PowerShell, we can just run the python/streamlit from inside .venv directly
$streamlitExe = ".\.venv\Scripts\streamlit.exe"
if (-not (Test-Path $streamlitExe)) {
    $streamlitExe = "streamlit"
}

& $streamlitExe run web/app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false

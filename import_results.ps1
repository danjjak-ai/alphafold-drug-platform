# MG Discovery Core - Import Colab Results (PowerShell version)
# Force UTF-8 Output Encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Host.UI.RawUI.WindowTitle = "MG Discovery Core - Import Colab Results"

Write-Host "`n--------------------------------------------------" -ForegroundColor Cyan
Write-Host "   MG Discovery Core - Results Importer" -ForegroundColor Cyan
Write-Host "--------------------------------------------------`n" -ForegroundColor Cyan

$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $currentDir

$zipFile = "discovery_results.zip"

if (-not (Test-Path $zipFile)) {
    Write-Host "[ERROR] $zipFile not found." -ForegroundColor Red
    Write-Host "        Please place the 'discovery_results.zip' file in the project root directory.`n" -ForegroundColor Yellow
    Read-Host "Press Enter to exit..."
    exit
}

Write-Host "[INFO] Extracting Colab results..." -ForegroundColor Cyan
try {
    Expand-Archive -Force -Path $zipFile -DestinationPath "."
    Write-Host "[SUCCESS] Result merging completed successfully!`n" -ForegroundColor Green
    
    # Cleanup
    Remove-Item $zipFile -Force
    Write-Host "[INFO] Temporary file ($zipFile) has been deleted." -ForegroundColor Gray
}
catch {
    Write-Host "[ERROR] Extraction failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nPlease execute 'start_dashboard.bat' to verify the results in the dashboard." -ForegroundColor White
Read-Host "Press Enter to exit..."

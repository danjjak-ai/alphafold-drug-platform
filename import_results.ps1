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
    Write-Host "[SUCCESS] Files extracted successfully!`n" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Extraction failed: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    exit
}

# ── 병명(disease) 메타데이터 읽기 ──────────────────────────────
$metaFile = "meta.json"
$diseaseName = $null

if (Test-Path $metaFile) {
    try {
        $meta = Get-Content $metaFile -Raw | ConvertFrom-Json
        $diseaseName = $meta.disease
        Write-Host "[INFO] Disease detected from meta.json: '$diseaseName'" -ForegroundColor Cyan
    }
    catch {
        Write-Host "[WARN] meta.json found but could not be parsed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}
else {
    Write-Host "[WARN] meta.json not found in zip. Please enter the disease name manually." -ForegroundColor Yellow
    $diseaseName = Read-Host "  Disease name (e.g. 'Myasthenia Gravis')"
}

if ($diseaseName) {
    # ── DB에 병명 등록 및 disease_id 연결 ──────────────────────
    Write-Host "[INFO] Registering disease and linking DB records..." -ForegroundColor Cyan
    $pythonExe = ".\.venv\Scripts\python.exe"
    if (-not (Test-Path $pythonExe)) {
        $pythonExe = "python"
    }

    $linkScript = @"
import sqlite3, os, sys

disease_name = sys.argv[1]
db_path = os.path.join('data', 'mg_discovery.db')

if not os.path.exists(db_path):
    print(f'[ERROR] DB not found: {db_path}')
    sys.exit(1)

conn = sqlite3.connect(db_path)
conn.execute('INSERT OR IGNORE INTO diseases (name) VALUES (?)', (disease_name,))
conn.commit()

row = conn.execute('SELECT id FROM diseases WHERE name = ?', (disease_name,)).fetchone()
if not row:
    print('[ERROR] Failed to register disease.')
    sys.exit(1)

disease_id = row[0]
print(f'[OK] Disease "{disease_name}" id={disease_id}')

# targets, compounds 에 disease_id 가 NULL 인 레코드를 일괄 업데이트
r1 = conn.execute('UPDATE targets SET disease_id = ? WHERE disease_id IS NULL', (disease_id,))
r2 = conn.execute('UPDATE compounds SET disease_id = ? WHERE disease_id IS NULL', (disease_id,))
conn.commit()
conn.close()
print(f'[OK] Linked {r1.rowcount} targets, {r2.rowcount} compounds to disease_id={disease_id}')
"@

    $tmpScript = [System.IO.Path]::Combine($currentDir, "_link_disease.py")
    Set-Content -Path $tmpScript -Value $linkScript -Encoding UTF8

    & $pythonExe $tmpScript $diseaseName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Disease '$diseaseName' linked to all imported records.`n" -ForegroundColor Green
    } else {
        Write-Host "[WARN] DB linking step failed. Check _link_disease.py output above." -ForegroundColor Yellow
    }

    Remove-Item $tmpScript -Force -ErrorAction SilentlyContinue
}
else {
    Write-Host "[WARN] No disease name provided. Records will not be linked to a disease." -ForegroundColor Yellow
}

# ── Cleanup ────────────────────────────────────────────────────
Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
Write-Host "[INFO] Temporary file ($zipFile) has been deleted." -ForegroundColor Gray

if (Test-Path $metaFile) {
    Remove-Item $metaFile -Force -ErrorAction SilentlyContinue
    Write-Host "[INFO] meta.json cleaned up." -ForegroundColor Gray
}

Write-Host "`nPlease execute 'start_dashboard.bat' to verify the results in the dashboard." -ForegroundColor White
Read-Host "Press Enter to exit..."

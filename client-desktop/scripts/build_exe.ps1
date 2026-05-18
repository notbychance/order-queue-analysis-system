$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Resolve-Path (Join-Path $ScriptDir "..")

Set-Location $ProjectDir

Write-Host "Installing desktop development dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

Write-Host "Running tests..."
python -m pytest

Write-Host "Building Windows executable..."
python -m PyInstaller --noconfirm --clean QueueAnalysisDesktop.spec

Write-Host ""
Write-Host "Build completed."
Write-Host "Executable folder:"
Write-Host "  dist\QueueAnalysisDesktop"
Write-Host ""
Write-Host "Run:"
Write-Host "  dist\QueueAnalysisDesktop\QueueAnalysisDesktop.exe"
Write-Host ""
Write-Host "Optional: copy .env to dist\QueueAnalysisDesktop\.env if you need custom API_BASE_URL or storage settings."

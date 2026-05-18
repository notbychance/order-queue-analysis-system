@echo off
setlocal

cd /d "%~dp0.."

echo Installing desktop development dependencies...
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

python -m pip install -r requirements-dev.txt
if errorlevel 1 exit /b 1

echo Running tests...
python -m pytest
if errorlevel 1 exit /b 1

echo Building Windows executable...
python -m PyInstaller --noconfirm --clean QueueAnalysisDesktop.spec
if errorlevel 1 exit /b 1

echo.
echo Build completed.
echo Executable folder:
echo   dist\QueueAnalysisDesktop
echo.
echo Run:
echo   dist\QueueAnalysisDesktop\QueueAnalysisDesktop.exe
echo.
echo Optional: copy .env to dist\QueueAnalysisDesktop\.env if you need custom API_BASE_URL or storage settings.

endlocal

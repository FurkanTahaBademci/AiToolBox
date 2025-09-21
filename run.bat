@echo off
echo ========================================
echo   AI ToolBox
echo   Starting Application...
echo ========================================

REM Python kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Gereksinimler kontrolü
echo Checking requirements...
pip install -r requirements.txt

REM Uygulama başlatma
echo Starting AI ToolBox...
python main.py

echo Application closed.
pause

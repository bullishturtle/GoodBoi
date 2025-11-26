@echo off
REM GoodBoy.AI Desktop UI Launcher
echo ========================================
echo   GoodBoy.AI - Starting Desktop UI
echo ========================================
echo.

cd /d "%~dp0"

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

REM Activate venv if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo [INFO] Starting GoodBoy.AI Desktop UI...
python GoodBoy_ui.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start UI
    echo Check that all dependencies are installed
    pause
)

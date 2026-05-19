@echo off
REM Simplified GoodBoy.AI Launcher

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Start server
start "GoodBoy.AI Server" /MIN cmd /c run_server.bat

REM Launch UI
python GoodBoy_ui.py
if errorlevel 1 (
    echo [ERROR] Failed to launch UI!
    pause
    exit /b 1
)

echo GoodBoy.AI is running!

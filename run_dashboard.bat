@echo off
REM GoodBoy.AI - Bathy City Dashboard Launcher
cd /d "%~dp0"

echo ================================================
echo   GoodBoy.AI - Command Center Dashboard
echo ================================================
echo.

if not exist venv (
    echo [GoodBoy.AI] venv not found. Run setup.ps1 first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [GoodBoy.AI] Starting Gradio dashboard on http://127.0.0.1:7860
echo [GoodBoy.AI] Make sure the server is running (run_server.bat)
echo.
python app/dashboard.py

pause

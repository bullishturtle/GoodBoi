@echo off
REM GoodBoy.AI - Desktop UI Launcher
cd /d "%~dp0"

echo ================================================
echo   GoodBoy.AI - Desktop Console
echo   Bathy City at Your Service
echo ================================================
echo.

REM Python check
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM First-time setup check
if not exist venv (
    echo [FIRST RUN] Setting up GoodBoy.AI...
    echo This will take a few minutes...
    echo.
    powershell -ExecutionPolicy Bypass -File setup.ps1
    if %errorlevel% neq 0 (
        echo [ERROR] Setup failed
        pause
        exit /b 1
    )
    echo.
    echo Setup complete! Starting GoodBoy.AI...
    echo.
)

call venv\Scripts\activate.bat

REM Start server in background if not running
echo [GoodBoy.AI] Checking for Bathy server...
python -c "import httpx; httpx.get('http://127.0.0.1:8000/health', timeout=2)" 2>nul
if %errorlevel% neq 0 (
    echo [GoodBoy.AI] Starting Bathy server in background...
    start "GoodBoy.AI Server" /MIN cmd /c run_server.bat
    timeout /t 3 /nobreak >nul
) else (
    echo [GoodBoy.AI] Server already running
)

echo [GoodBoy.AI] Launching desktop UI...
echo [GoodBoy.AI] Tip: Start run_server.bat first for full council mode
echo.
python GoodBoy_ui.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] UI failed to start
    pause
)

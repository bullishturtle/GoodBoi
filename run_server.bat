@echo off
REM GoodBoy.AI - Bathy City Server Launcher
cd /d "%~dp0"

echo ================================================
echo   GoodBoy.AI - Bathy City Server
echo   Self-Aware, Self-Learning AI Assistant
echo ================================================
echo.

REM Better error checking and handling
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check for venv and create if missing
if not exist venv (
    echo [WARNING] Virtual environment not found
    echo Running setup.ps1 to create it...
    echo.
    powershell -ExecutionPolicy Bypass -File setup.ps1
    if %errorlevel% neq 0 (
        echo [ERROR] Setup failed
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

REM Verify FastAPI is installed
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] FastAPI not installed, installing dependencies...
    pip install -r requirements.txt --quiet
)

echo [GoodBoy.AI] Starting FastAPI server on http://127.0.0.1:8000
echo [GoodBoy.AI] Press Ctrl+C to stop
echo.

REM Use python -m uvicorn for better compatibility
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server failed to start
    echo Check logs above for errors
    pause
)

@echo off
REM Simplified GoodBoy.AI Installer

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Install dependencies
pip install --quiet --upgrade pip
pip install --quiet pyinstaller

REM Build executable
pyinstaller --name=GoodBoy --onedir --windowed --noconfirm GoodBoy_ui.py
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo Build complete! Executable is in the dist folder.
pause

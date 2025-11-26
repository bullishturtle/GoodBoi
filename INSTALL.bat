@echo off
echo ============================================================
echo GoodBoy.AI Installer
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Running installer...
python install.py

echo.
echo ============================================================
echo Installation complete!
echo ============================================================
echo.
echo Run 'GoodBoy_launcher.bat' to start
pause

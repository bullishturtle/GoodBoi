@echo off
REM GoodBoy.AI - Build Desktop Executable
cd /d "%~dp0"

echo ================================================
echo   GoodBoy.AI - Building Desktop Executable
echo ================================================
echo.

if not exist venv (
    echo [GoodBoy.AI] venv not found. Run setup.ps1 first.
    exit /b 1
)

call venv\Scripts\activate.bat

REM Install PyInstaller if not present
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [GoodBoy.AI] Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Create assets directory if needed
if not exist assets (
    mkdir assets
    echo [GoodBoy.AI] Created assets directory
    echo [GoodBoy.AI] Add goodboy_icon.ico and goodboy_logo.png for branding
)

echo [GoodBoy.AI] Building GoodBoy desktop executable...
pyinstaller --noconfirm ^
  --name GoodBoyDesktop ^
  --windowed ^
  --add-data "data;data" ^
  --add-data "memory;memory" ^
  --add-data "assets;assets" ^
  --add-data "app;app" ^
  GoodBoy_ui.py

if errorlevel 1 (
    echo [GoodBoy.AI] Build failed!
    pause
    exit /b 1
)

echo.
echo ================================================
echo   Build Complete!
echo ================================================
echo.
echo [GoodBoy.AI] Executable is in: dist\GoodBoyDesktop\
echo [GoodBoy.AI] Run: dist\GoodBoyDesktop\GoodBoyDesktop.exe
echo.
pause

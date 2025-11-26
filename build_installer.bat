@echo off
REM GoodBoy.AI Build Script - Creates distributable installer
REM Requires: Python 3.10+, PyInstaller, Inno Setup 6

echo ========================================
echo   GoodBoy.AI Build System
echo ========================================
echo.

REM Check for virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Run setup.ps1 first.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo [1/4] Installing build dependencies...
pip install pyinstaller --quiet

echo [2/4] Building executable with PyInstaller...
pyinstaller ^
    --name=GoodBoy ^
    --onedir ^
    --windowed ^
    --icon=assets\goodboy_icon.ico ^
    --add-data "data;data" ^
    --add-data "app;app" ^
    --hidden-import=gpt4all ^
    --hidden-import=uvicorn ^
    --hidden-import=fastapi ^
    --hidden-import=gradio ^
    --hidden-import=pydantic ^
    --hidden-import=requests ^
    --hidden-import=tkinter ^
    --collect-all gpt4all ^
    --collect-all gradio ^
    --noconfirm ^
    --clean ^
    GoodBoy_ui.py

if errorlevel 1 (
    echo [ERROR] PyInstaller build failed!
    pause
    exit /b 1
)

echo [3/4] Copying additional files...
if not exist "dist\GoodBoy\models" mkdir "dist\GoodBoy\models"
if not exist "dist\GoodBoy\data" mkdir "dist\GoodBoy\data"
if not exist "dist\GoodBoy\logs" mkdir "dist\GoodBoy\logs"

REM Copy config templates
copy "data\GoodBoy_config.json" "dist\GoodBoy\data\" >nul 2>&1
copy "data\Behavior_instructions.json" "dist\GoodBoy\data\" >nul 2>&1

echo [4/4] Building installer with Inno Setup...
REM Check if Inno Setup is installed
where iscc >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Inno Setup not found. Skipping installer creation.
    echo           Download from: https://jrsoftware.org/isinfo.php
    echo.
    echo Build complete! Portable version available in: dist\GoodBoy\
) else (
    iscc "installer\GoodBoy_installer.iss"
    if errorlevel 1 (
        echo [ERROR] Inno Setup build failed!
    ) else (
        echo.
        echo ========================================
        echo   BUILD COMPLETE!
        echo ========================================
        echo.
        echo Portable: dist\GoodBoy\GoodBoy.exe
        echo Installer: dist\GoodBoy_Setup_1.0.0.exe
    )
)

echo.
pause

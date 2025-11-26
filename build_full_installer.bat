@echo off
REM Complete build script for GoodBoy.AI installer

echo ============================================
echo GoodBoy.AI Complete Installer Build
echo ============================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [1/6] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] No virtual environment found. Using system Python.
)

echo.
echo [2/6] Installing/updating dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [3/6] Building Desktop UI executable...
pyinstaller --clean --noconfirm GoodBoy_ui.spec
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Desktop UI build failed!
    pause
    exit /b 1
)

echo.
echo [4/6] Building Backend Server executable...
pyinstaller --clean --noconfirm GoodBoy_server.spec
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Server build failed!
    pause
    exit /b 1
)

echo.
echo [5/6] Verifying builds...
if not exist "dist\GoodBoy\GoodBoy.exe" (
    echo [ERROR] GoodBoy.exe not found!
    pause
    exit /b 1
)
if not exist "dist\GoodBoyServer\GoodBoyServer.exe" (
    echo [ERROR] GoodBoyServer.exe not found!
    pause
    exit /b 1
)

echo.
echo [6/6] Creating installer with Inno Setup...
REM Check for Inno Setup
set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %INNO_PATH% (
    set INNO_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not exist %INNO_PATH% (
    echo [WARNING] Inno Setup not found. Please install from: https://jrsoftware.org/isdl.php
    echo.
    echo Executables are ready in the 'dist' folder.
    echo After installing Inno Setup, run: ISCC.exe installer\GoodBoy_installer.iss
    pause
    exit /b 0
)

%INNO_PATH% "installer\GoodBoy_installer.iss"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Installer creation failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo BUILD COMPLETE!
echo ============================================
echo.
echo Installer location: dist\installer\GoodBoy_AI_Setup.exe
echo.
echo You can now distribute GoodBoy_AI_Setup.exe
echo.
pause

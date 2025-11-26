# GoodBoy.AI Build & Distribution Guide

Complete guide for building and distributing GoodBoy.AI desktop application.

## Prerequisites

### Required Software
1. **Python 3.10+** - https://www.python.org/downloads/
2. **PyInstaller** - Installed via pip
3. **Inno Setup 6** - https://jrsoftware.org/isdl.php (for Windows installer)

### Optional Tools
- **UPX** - https://upx.github.io/ (executable compression)
- **Resource Hacker** - Icon editing for exe files

## Build Process

### Step 1: Environment Setup

\`\`\`powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
\`\`\`

### Step 2: Build Executables

\`\`\`powershell
# Build Desktop UI
pyinstaller --clean --noconfirm GoodBoy_ui.spec

# Build Backend Server
pyinstaller --clean --noconfirm GoodBoy_server.spec
\`\`\`

This creates:
- `dist/GoodBoy/GoodBoy.exe` - Desktop UI application
- `dist/GoodBoyServer/GoodBoyServer.exe` - Backend server

### Step 3: Create Installer (Windows)

\`\`\`powershell
# Using the automated script
.\build_full_installer.bat

# Or manually with Inno Setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\GoodBoy_installer.iss
\`\`\`

Result: `dist/installer/GoodBoy_AI_Setup.exe`

## Quick Build (All-in-One)

\`\`\`powershell
.\build_full_installer.bat
\`\`\`

This script:
1. Activates virtual environment
2. Installs/updates dependencies
3. Builds both executables
4. Creates Windows installer
5. Verifies all builds

## Manual Testing

### Test Desktop UI
\`\`\`powershell
cd dist\GoodBoy
.\GoodBoy.exe
\`\`\`

### Test Backend Server
\`\`\`powershell
cd dist\GoodBoyServer
.\GoodBoyServer.exe
\`\`\`

### Test Installer
\`\`\`powershell
dist\installer\GoodBoy_AI_Setup.exe
\`\`\`

## File Structure

\`\`\`
dist/
├── GoodBoy/              # Desktop UI build
│   ├── GoodBoy.exe
│   ├── data/
│   ├── memory/
│   └── ...
├── GoodBoyServer/        # Backend server build
│   ├── GoodBoyServer.exe
│   ├── app/
│   └── ...
└── installer/            # Final installer
    └── GoodBoy_AI_Setup.exe
\`\`\`

## Customization

### Change Icon
1. Replace `assets/goodboy_icon.ico` with your icon (256x256 recommended)
2. Rebuild with PyInstaller

### Modify Installer
Edit `installer/GoodBoy_installer.iss`:
- App name, version, publisher
- Installation directory
- Start menu items
- Desktop/startup shortcuts

### Add Dependencies
1. Update `requirements.txt`
2. Add to `hiddenimports` in `.spec` files
3. Rebuild

## Distribution

### Single Installer
- **File**: `GoodBoy_AI_Setup.exe`
- **Size**: ~100-200MB (without models)
- **Contains**: Everything needed to run GoodBoy.AI

### Portable Version
Create a ZIP of `dist/GoodBoy` + `dist/GoodBoyServer` for users who prefer portable apps.

### Model Distribution
Models are NOT included in the installer (too large).  
Users download models on first run via the Model Manager.

## Troubleshooting

### "Failed to execute script"
- Check `hiddenimports` in `.spec` files
- Verify all dependencies are installed
- Test in clean virtual environment

### "DLL load failed"
- Missing system libraries (rare on Windows 10/11)
- Install Visual C++ Redistributable
- Check antivirus blocking

### Large EXE Size
- Remove unnecessary dependencies
- Use UPX compression
- Exclude unused libraries in `.spec` files

### Antivirus False Positives
- Sign your executables (requires code signing certificate)
- Submit to antivirus vendors for whitelisting
- Use official PyInstaller bootloader

## Code Signing (Optional)

For production distribution:

\`\`\`powershell
# Sign executables
signtool sign /f certificate.pfx /p password /t http://timestamp.server /d "GoodBoy.AI" dist\GoodBoy\GoodBoy.exe
signtool sign /f certificate.pfx /p password /t http://timestamp.server /d "GoodBoy.AI Server" dist\GoodBoyServer\GoodBoyServer.exe

# Sign installer
signtool sign /f certificate.pfx /p password /t http://timestamp.server /d "GoodBoy.AI Setup" dist\installer\GoodBoy_AI_Setup.exe
\`\`\`

## Continuous Integration

Example GitHub Actions workflow:

\`\`\`yaml
name: Build GoodBoy.AI

on: [push]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller --clean GoodBoy_ui.spec
      - run: pyinstaller --clean GoodBoy_server.spec
      - uses: actions/upload-artifact@v3
        with:
          name: GoodBoy-Windows
          path: dist/
\`\`\`

## Updates & Versioning

Update version in multiple places:
1. `installer/GoodBoy_installer.iss` - `#define MyAppVersion`
2. `app/main.py` - `version="x.x.x"`
3. `README.md`
4. `GoodBoy_ui.py` - Window title

## Support

For build issues:
1. Check `build_full_installer.bat` output
2. Review PyInstaller warnings
3. Test in clean environment
4. Check GitHub issues

---

**Ready to build?** Run `.\build_full_installer.bat` and you're done!

# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for GoodBoy.AI Desktop UI

block_cipher = None

added_files = [
    ('data', 'data'),
    ('memory', 'memory'),
    ('models', 'models'),
    ('assets', 'assets'),
    ('logs', 'logs'),
]

a = Analysis(
    ['GoodBoy_ui.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'httpx',
        'tkinter',
        'gpt4all',
        'app.teachings',
        'app.model_manager',
        'pypdf',
        'docx',
        'pyttsx3',
        'sounddevice',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GoodBoy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/goodboy_icon.ico' if Path('assets/goodboy_icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GoodBoy',
)

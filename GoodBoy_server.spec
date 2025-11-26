# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for GoodBoy.AI Backend Server

block_cipher = None

added_files = [
    ('app', 'app'),
    ('data', 'data'),
    ('memory', 'memory'),
    ('models', 'models'),
]

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'uvicorn.lifespan.on',
        'uvicorn.loops.auto',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets.auto',
        'httpx',
        'pydantic',
        'gpt4all',
        'chromadb',
        'sentence_transformers',
        'app.council',
        'app.agents.batman',
        'app.agents.alfred',
        'app.agents.jarvis',
        'app.agents.davinci',
        'app.agents.architect',
        'app.agents.analyst',
        'app.memory',
        'app.memory_evolution',
        'app.learning_engine',
        'app.mini_bot_nursery',
        'app.teachings',
        'app.llm',
        'app.tools',
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
    name='GoodBoyServer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console for server logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GoodBoyServer',
)

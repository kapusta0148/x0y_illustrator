# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['x0y_illustrator_main.py'],
    pathex=[],
    binaries=[],
    datas=[('x0y illustrator.ui', '.'), ('intervals_of_monotonicity.py', '.'), ('int_numbers.py', '.'), ('database_utils.py', '.'), ('analiz.py', '.'), ('loading.gif', '.'), ('History_of_req.sqlite', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='x0y_illustrator_main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

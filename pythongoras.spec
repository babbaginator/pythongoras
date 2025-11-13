# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\neila\\Dropbox\\Projects\\_Code\\PythonProjects\\pythongoras\\pythongoras.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\neila\\Dropbox\\Projects\\_Code\\PythonProjects\\pythongoras\\IMFePIrm28P.ttf', '.'), ('C:\\Users\\neila\\Dropbox\\Projects\\_Code\\PythonProjects\\pythongoras\\NotoSans-Regular.ttf', '.'), ('C:\\Users\\neila\\Dropbox\\Projects\\_Code\\PythonProjects\\pythongoras\\SigmarOne-Regular.ttf', '.'), ('C:\\Users\\neila\\Dropbox\\Projects\\_Code\\PythonProjects\\pythongoras\\config.txt', '.'), ('C:\\Users\\neila\\Dropbox\\Projects\\_Code\\PythonProjects\\pythongoras\\data', 'data/')],
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
    name='pythongoras',
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
    icon=['C:\\Users\\neila\\Dropbox\\Projects\\_Code\\PythonProjects\\pythongoras\\pythongoras.ico'],
)

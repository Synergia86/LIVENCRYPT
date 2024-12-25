a = Analysis(
    ['LIVENCRYPT1.1.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/synergia/Escritorio/icono.png', '.')], #Poner ruta donde lo descargues
    hiddenimports=['PIL', 'PIL._imaging', 'PIL._tkinter_finder', 'PIL.ImageTk', 'PIL._imagingtk'],
    hookspath=['hook-PIL.py'],
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
    name='LIVENCRYPT1.1',
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

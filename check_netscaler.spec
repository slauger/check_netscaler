# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for check_netscaler
Creates a single-file executable for cross-platform distribution
"""

block_cipher = None

a = Analysis(
    ['run_check_netscaler.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'check_netscaler.client',
        'check_netscaler.client.session',
        'check_netscaler.client.nitro',
        'check_netscaler.client.exceptions',
        'check_netscaler.commands',
        'check_netscaler.commands.base',
        'check_netscaler.commands.state',
        'check_netscaler.commands.threshold',
        'check_netscaler.commands.sslcert',
        'check_netscaler.commands.nsconfig',
        'check_netscaler.commands.hwinfo',
        'check_netscaler.commands.hastatus',
        'check_netscaler.commands.license',
        'check_netscaler.commands.interfaces',
        'check_netscaler.commands.perfdata',
        'check_netscaler.commands.servicegroup',
        'check_netscaler.commands.matches',
        'check_netscaler.commands.staserver',
        'check_netscaler.commands.ntp',
        'check_netscaler.commands.debug',
        'check_netscaler.output',
        'check_netscaler.output.nagios',
        'check_netscaler.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'pytest-cov',
        'pytest-mock',
        'black',
        'ruff',
        'mypy',
        'setuptools',
        '_pytest',
        'py',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='check_netscaler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

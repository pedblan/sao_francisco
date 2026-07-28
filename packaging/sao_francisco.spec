# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller recipe for the native Apple Silicon application bundle."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


PROJECT_ROOT = Path(SPECPATH).resolve().parent
PACKAGE_ROOT = PROJECT_ROOT / "sao_francisco"
APP_NAME = "São Francisco"
EXECUTABLE_NAME = "sao-francisco"
APP_ICON = PACKAGE_ROOT / "assets" / "branding" / "sao-francisco-macos.png"

datas = [
    (str(PACKAGE_ROOT / "AJUDA.md"), "sao_francisco"),
    (str(PACKAGE_ROOT / "THIRD_PARTY_NOTICES.md"), "sao_francisco"),
    (str(PACKAGE_ROOT / "assets"), "sao_francisco/assets"),
    (str(PACKAGE_ROOT / "licenses"), "sao_francisco/licenses"),
    (str(PACKAGE_ROOT / "qml"), "sao_francisco/qml"),
]
hiddenimports = sorted(
    {
        "Security",
        *collect_submodules("google.genai"),
        *collect_submodules("openai"),
        *collect_submodules("yt_dlp"),
    }
)

a = Analysis(
    [str(PACKAGE_ROOT / "__main__.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[str(PROJECT_ROOT / "packaging" / "hooks")],
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
    [],
    exclude_binaries=True,
    name=EXECUTABLE_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    target_arch="arm64",
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=APP_NAME,
)
app = BUNDLE(
    coll,
    name=f"{APP_NAME}.app",
    icon=str(APP_ICON),
    bundle_identifier="com.pedblan.saofrancisco",
    info_plist={
        "CFBundleDisplayName": APP_NAME,
        "CFBundleName": APP_NAME,
        "CFBundleShortVersionString": "0.1.0",
        "CFBundleVersion": "1",
        "LSApplicationCategoryType": "public.app-category.utilities",
        "LSArchitecturePriority": ["arm64"],
        "LSMinimumSystemVersion": "12.0",
        "NSHighResolutionCapable": True,
    },
)

#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Este build precisa ser executado no macOS." >&2
    exit 1
fi

if [[ "$(uname -m)" != "arm64" ]]; then
    echo "Este build precisa ser executado nativamente em Apple Silicon." >&2
    exit 1
fi

python_bin="${PYTHON_BIN:-/opt/homebrew/bin/python3}"
if [[ ! -x "$python_bin" ]]; then
    echo "Python ARM64 não encontrado em $python_bin." >&2
    echo "Defina PYTHON_BIN com o caminho de um Python 3.11–3.13 nativo." >&2
    exit 1
fi

python_arch="$("$python_bin" -c 'import platform; print(platform.machine())')"
if [[ "$python_arch" != "arm64" ]]; then
    echo "O Python selecionado não é ARM64: $python_arch." >&2
    exit 1
fi

temporary_root="$(mktemp -d "${TMPDIR:-/tmp}/sao-francisco-arm64.XXXXXX")"
build_venv="${BUILD_VENV:-/private/tmp/sao-francisco-macos-arm64-venv}"
build_dist="$temporary_root/dist"
build_work="$temporary_root/work"
dmg_root="$temporary_root/dmg"
zip_verify_root="$temporary_root/zip-verify"

cleanup() {
    if [[ "${KEEP_BUILD_TEMP:-0}" == "1" ]]; then
        echo "Diretório temporário preservado em: $temporary_root"
        return
    fi
    if [[ -n "${temporary_root:-}" && -d "$temporary_root" ]]; then
        rm -rf "$temporary_root"
    fi
}
trap cleanup EXIT

if [[ ! -x "$build_venv/bin/python" ]]; then
    "$python_bin" -m venv "$build_venv"
fi
"$build_venv/bin/python" -m pip install --upgrade pip
"$build_venv/bin/python" -m pip install \
    -r requirements.txt \
    "pillow>=11,<13" \
    "pyinstaller>=6.14,<7"

export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-12.0}"
"$build_venv/bin/python" -m PyInstaller \
    --noconfirm \
    --clean \
    --distpath "$build_dist" \
    --workpath "$build_work" \
    packaging/sao_francisco.spec

built_app="$build_dist/São Francisco.app"
version="$("$build_venv/bin/python" -c 'from sao_francisco import __version__; print(__version__)')"
zip_path="$project_root/dist/Sao-Francisco-${version}-macos-arm64.zip"
dmg_path="$project_root/dist/Sao-Francisco-${version}-macos-arm64.dmg"

if [[ -f "$zip_path" ]]; then
    rm -f "$zip_path"
fi
xattr -cr "$built_app"
find "$built_app" -type l -exec xattr -s -c '{}' \;

# PyInstaller normally seals the complete bundle. Keep a staged fallback for
# macOS releases on which its single recursive codesign invocation can fail.
if ! codesign --verify --deep --strict "$built_app" 2>/dev/null; then
    codesign --remove-signature "$built_app" 2>/dev/null || true
    find "$built_app/Contents" -depth -type d \
        \( -name '*.framework' -o -name '*.app' -o -name '*.bundle' \) \
        -print0 |
        while IFS= read -r -d '' nested_bundle; do
            codesign --force --sign - --timestamp=none "$nested_bundle"
        done
    main_executable="$built_app/Contents/MacOS/sao-francisco"
    staged_executable="$temporary_root/sao-francisco-main"
    cp "$main_executable" "$staged_executable"
    codesign --remove-signature "$staged_executable" 2>/dev/null || true
    codesign --force --sign - --timestamp=none "$staged_executable"
    cp "$staged_executable" "$main_executable"
    codesign --force --sign - --timestamp=none "$built_app"
fi
codesign --verify --deep --strict --verbose=1 "$built_app"

"$built_app/Contents/MacOS/sao-francisco" --smoke-test
"$built_app/Contents/MacOS/sao-francisco" --yt-dlp --version >/dev/null

mkdir -p "$dmg_root"
ditto "$built_app" "$dmg_root/São Francisco.app"
ln -s /Applications "$dmg_root/Applications"
hdiutil create \
    -volname "São Francisco" \
    -srcfolder "$dmg_root" \
    -ov \
    -format UDZO \
    "$dmg_path"

ditto -c -k --sequesterRsrc --keepParent "$built_app" "$zip_path"
mkdir -p "$zip_verify_root"
ditto -x -k "$zip_path" "$zip_verify_root"
codesign --verify --deep --strict --verbose=1 \
    "$zip_verify_root/São Francisco.app"

if [[ -d "$project_root/dist/macos-arm64" ]]; then
    rm -rf "$project_root/dist/macos-arm64"
fi

echo
echo "Build Apple Silicon concluído:"
echo "  ZIP:        $zip_path"
echo "  DMG:        $dmg_path"

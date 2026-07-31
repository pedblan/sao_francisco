from __future__ import annotations

import re
import tomllib
from pathlib import Path

from sao_francisco import __version__


def test_release_version_is_synchronized() -> None:
    project_root = Path(__file__).resolve().parents[1]
    pyproject = tomllib.loads(
        (project_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    macos_spec = (project_root / "packaging/sao_francisco.spec").read_text(
        encoding="utf-8"
    )
    windows_script = (project_root / "scripts/build_windows_x64.ps1").read_text(
        encoding="utf-8"
    )
    windows_workflow = (
        project_root / ".github/workflows/windows-release.yml"
    ).read_text(encoding="utf-8")

    assert __version__ == "0.1.2"
    assert pyproject["project"]["version"] == __version__
    assert re.search(
        rf'"CFBundleShortVersionString": "{re.escape(__version__)}"',
        macos_spec,
    )
    assert "0.1.1" not in macos_spec
    assert "0.1.1" not in windows_script
    assert "0.1.1" not in windows_workflow

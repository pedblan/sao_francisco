"""Collect only the Qt QML modules used by São Francisco.

PyInstaller's stock PySide6.QtQml hook includes every QML module shipped with
PySide6.  Besides making this small desktop app unnecessarily large, that
would pull QtWebEngine and its nested helper app into the macOS bundle.
"""

from pathlib import PurePosixPath

from PyInstaller.utils.hooks.qt import (
    add_qt6_dependencies,
    pyside6_library_info,
)

_QML_ROOT = PurePosixPath("PySide6/Qt/qml")
def _is_used_qml_module(item: tuple[str, str]) -> bool:
    destination = PurePosixPath(item[1])
    try:
        relative_parts = destination.relative_to(_QML_ROOT).parts
    except ValueError:
        return False

    if relative_parts == ("QtCore",):
        return True
    if relative_parts and relative_parts[0] == "QtQml":
        return len(relative_parts) == 1 or relative_parts[1] in {
            "Models",
            "WorkerScript",
        }
    if not relative_parts or relative_parts[0] != "QtQuick":
        return False
    if len(relative_parts) == 1:
        return True
    if relative_parts[1] in {"Window", "Layouts", "Templates", "Dialogs"}:
        return True
    if relative_parts[1] != "Controls":
        return False
    return len(relative_parts) == 2 or relative_parts[2] in {
        "impl",
        "Basic",
        "Fusion",
    }


hiddenimports, binaries, datas = add_qt6_dependencies(__file__)
qml_binaries, qml_datas = pyside6_library_info.collect_qtqml_files()
binaries += [item for item in qml_binaries if _is_used_qml_module(item)]
datas += [item for item in qml_datas if _is_used_qml_module(item)]

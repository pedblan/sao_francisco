"""Executable Qt launcher for São Francisco."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any


def _report_startup_error(message: str) -> None:
    """Report an early launcher failure even when a GUI script has no stderr."""

    stream = sys.stderr
    if stream is not None:
        try:
            stream.write(message.rstrip() + "\n")
            return
        except (OSError, RuntimeError):
            pass
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(  # type: ignore[attr-defined]
                None,
                message,
                "São Francisco",
                0x10,
            )
        except (AttributeError, OSError):
            pass


def main(argv: Sequence[str] | None = None) -> int:
    """Create the Qt application, inject ``appBackend``, and load ``Main.qml``."""

    try:
        from PySide6.QtCore import QCoreApplication, QRect, QSettings, QUrl
        from PySide6.QtGui import QFontDatabase, QIcon
        from PySide6.QtQml import QQmlApplicationEngine
        from PySide6.QtQuick import QQuickWindow
        from PySide6.QtQuickControls2 import QQuickStyle
        from PySide6.QtWidgets import QApplication, QMessageBox
    except ImportError:
        _report_startup_error(
            "São Francisco requer PySide6. Reinstale o aplicativo para restaurar o Qt 6."
        )
        return 2

    from . import __version__
    from .backend import AppBackend

    QCoreApplication.setOrganizationName("São Francisco")
    QCoreApplication.setOrganizationDomain("sao-francisco.local")
    QCoreApplication.setApplicationName("São Francisco")
    QCoreApplication.setApplicationVersion(__version__)
    QQuickStyle.setStyle("Fusion")

    arguments = list(argv) if argv is not None else list(sys.argv)
    application = QApplication(arguments)
    application.setApplicationDisplayName("São Francisco")
    application.setQuitOnLastWindowClosed(True)

    package_root = Path(__file__).resolve().parent
    _register_fonts(QFontDatabase, package_root / "assets" / "fonts")
    icon_path = package_root / "assets" / "branding" / "sao-francisco-bauhaus.svg"
    if icon_path.is_file():
        application.setWindowIcon(QIcon(str(icon_path)))

    settings = QSettings()
    backend = AppBackend(qsettings=settings, parent=application)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appBackend", backend)
    engine.load(QUrl.fromLocalFile(str(package_root / "qml" / "Main.qml")))
    roots = engine.rootObjects()
    if not roots:
        backend.shutdown()
        message = "Não foi possível carregar a interface do São Francisco."
        QMessageBox.critical(None, "São Francisco", message)
        _report_startup_error(message)
        return 1

    window = roots[0]
    if isinstance(window, QQuickWindow):
        _restore_window(window, settings, QRect, QApplication)

    geometry_saved = False

    def save_before_hide(*_args: object) -> None:
        nonlocal geometry_saved
        if isinstance(window, QQuickWindow):
            _save_window(window, settings)
            geometry_saved = True

    if isinstance(window, QQuickWindow):
        window.closing.connect(save_before_hide)

    def finish() -> None:
        if not geometry_saved:
            save_before_hide()
        backend.shutdown()

    application.aboutToQuit.connect(finish)
    return int(application.exec())


def _register_fonts(font_database: Any, directory: Path) -> None:
    for name in (
        "Jost-Variable.ttf",
        "Jost-Italic-Variable.ttf",
        "SourceSans3-Variable.ttf",
        "SourceSans3-Italic-Variable.ttf",
    ):
        path = directory / name
        if path.is_file():
            font_database.addApplicationFont(str(path))


def _restore_window(
    window: Any,
    settings: Any,
    rect_type: Any,
    application_type: Any,
) -> None:
    if not settings.value(
        "preferences/rememberWindowGeometry",
        True,
        type=bool,
    ):
        return
    width = settings.value("window/width", 1280, type=int)
    height = settings.value("window/height", 800, type=int)
    x = settings.value("window/x", -1, type=int)
    y = settings.value("window/y", -1, type=int)
    candidate = rect_type(x, y, max(1024, width), max(680, height))
    screens = application_type.screens()
    if (
        x >= 0
        and y >= 0
        and any(screen.availableGeometry().intersects(candidate) for screen in screens)
    ):
        window.setGeometry(candidate)
    else:
        screen = window.screen() or application_type.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            restored_width = min(candidate.width(), available.width())
            restored_height = min(candidate.height(), available.height())
            window.setGeometry(
                available.x() + (available.width() - restored_width) // 2,
                available.y() + (available.height() - restored_height) // 2,
                restored_width,
                restored_height,
            )
    if settings.value("window/maximized", False, type=bool):
        window.showMaximized()


def _save_window(window: Any, settings: Any) -> None:
    if not settings.value(
        "preferences/rememberWindowGeometry",
        True,
        type=bool,
    ):
        settings.remove("window")
        settings.sync()
        return
    visibility = window.visibility()
    maximized = visibility == type(visibility).Maximized
    if not maximized:
        geometry = window.geometry()
        settings.setValue("window/x", geometry.x())
        settings.setValue("window/y", geometry.y())
        settings.setValue("window/width", geometry.width())
        settings.setValue("window/height", geometry.height())
    settings.setValue("window/maximized", maximized)
    settings.sync()


if __name__ == "__main__":
    raise SystemExit(main())

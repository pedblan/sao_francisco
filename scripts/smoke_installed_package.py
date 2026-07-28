"""Smoke test a built São Francisco wheel outside the source checkout."""

# ruff: noqa: E402

from __future__ import annotations

import os
import tempfile
from importlib.metadata import distribution
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Fusion")

from PySide6.QtCore import QCoreApplication, QEvent, QSettings, QUrl
from PySide6.QtGui import QFontDatabase
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

import sao_francisco
from sao_francisco.backend import AppBackend


def main() -> int:
    entry_points = distribution("sao-francisco").entry_points
    launcher = next(
        (
            item
            for item in entry_points
            if item.group == "gui_scripts" and item.name == "sao-francisco"
        ),
        None,
    )
    if launcher is None or launcher.value != "sao_francisco.app:main":
        raise RuntimeError("O wheel não contém o launcher gráfico sao-francisco.")

    package_root = Path(sao_francisco.__file__).resolve().parent
    required = (
        package_root / "AJUDA.md",
        package_root / "THIRD_PARTY_NOTICES.md",
        package_root / "qml" / "Main.qml",
        package_root / "assets" / "branding" / "sao-francisco-bauhaus.svg",
        package_root / "assets" / "fonts" / "Jost-Variable.ttf",
        package_root / "assets" / "fonts" / "SourceSans3-Variable.ttf",
    )
    missing = tuple(path for path in required if not path.is_file())
    if missing:
        raise RuntimeError(f"Arquivos ausentes no wheel: {missing}")

    QQuickStyle.setStyle("Fusion")
    application = QApplication.instance() or QApplication([])
    for font_path in (package_root / "assets" / "fonts").glob("*.ttf"):
        if QFontDatabase.addApplicationFont(str(font_path)) < 0:
            raise RuntimeError(f"Não foi possível registrar {font_path.name}")

    with tempfile.TemporaryDirectory(prefix="sao-francisco-wheel-smoke-") as temporary:
        temporary_root = Path(temporary)
        settings = QSettings(
            str(temporary_root / "settings.ini"),
            QSettings.Format.IniFormat,
        )
        backend = AppBackend(
            qsettings=settings,
            data_root=temporary_root / "data",
            default_output_root=temporary_root / "output",
            parent=application,
        )
        engine = QQmlApplicationEngine()
        warnings: list[str] = []
        engine.warnings.connect(
            lambda messages: warnings.extend(message.toString() for message in messages)
        )
        engine.rootContext().setContextProperty("appBackend", backend)
        engine.load(QUrl.fromLocalFile(str(package_root / "qml" / "Main.qml")))
        application.processEvents()

        roots = engine.rootObjects()
        if not roots or not isinstance(roots[0], QQuickWindow):
            raise RuntimeError("O Main.qml do wheel não criou a janela principal.")
        if warnings:
            raise RuntimeError("Avisos ao carregar o wheel:\n" + "\n".join(warnings))

        window = roots[0]
        window.setWidth(1024)
        window.setHeight(680)
        window.show()
        application.processEvents()
        if window.width() != 1024 or window.height() != 680:
            raise RuntimeError("A janela instalada não respeitou o tamanho mínimo.")

        window.close()
        application.processEvents()
        if not backend.shutdown():
            raise RuntimeError("A thread de trabalho não encerrou no smoke test.")

        roots.clear()
        engine.deleteLater()
        backend.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        application.processEvents()

    QFontDatabase.removeAllApplicationFonts()
    application.processEvents()
    application.quit()
    print(f"wheel instalado validado: São Francisco {sao_francisco.__version__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

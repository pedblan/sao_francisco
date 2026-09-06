"""Render the real localized backend without network calls or personal settings."""

# ruff: noqa: E402, F811
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Fusion")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QMetaObject, QObject, QPointF, QSettings, Qt, QUrl
from PySide6.QtQml import QQmlApplicationEngine, QQmlExpression
from PySide6.QtQuick import QQuickItem, QQuickWindow
from PySide6.QtTest import QTest
from test_backend import FakePipeline
from test_qml_offscreen import (
    END_MARKERS,
    QML_MAIN,
    ROUTES,
    WINDOW_SIZES,
    _number,
    _quick_item,
    _scroll_to_end,
    _settle,
    qt_app,  # noqa: F401 - shared fixture
)

import sao_francisco.backend as backend_module
from sao_francisco.backend import AppBackend
from sao_francisco.i18n import LANGUAGES
from sao_francisco.qt_i18n import ProductTranslator


def _visual_item(root: QQuickItem, name: str) -> QQuickItem:
    pending = [root]
    while pending:
        item = pending.pop()
        if item.objectName() == name:
            return item
        pending.extend(item.childItems())
    raise AssertionError(name)


@pytest.mark.parametrize("locale", [code for code, _name in LANGUAGES])
def test_localized_routes_dialog_and_live_switch(qt_app, tmp_path: Path, monkeypatch, locale):
    monkeypatch.setattr(backend_module, "_masked_credential", lambda _provider: "")
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    backend = AppBackend(pipeline=FakePipeline(tmp_path), qsettings=settings)
    assert backend.interfaceLanguage == "en-US"
    assert backend.setInterfaceLanguage(locale)
    engine = QQmlApplicationEngine()
    translator = ProductTranslator(lambda: backend.localizer, qt_app)
    qt_app.installTranslator(translator)
    warnings = []
    engine.warnings.connect(lambda items: warnings.extend(item.toString() for item in items))

    def retranslate():
        qt_app.setLayoutDirection(Qt.RightToLeft if backend.rightToLeft else Qt.LeftToRight)
        engine.retranslate()

    backend.interfaceLanguageChanged.connect(retranslate)
    retranslate()
    engine.rootContext().setContextProperty("appBackend", backend)
    snapshots = Path(os.environ.get("SF_I18N_SCREENSHOTS", str(tmp_path))) / locale
    snapshots.mkdir(parents=True, exist_ok=True)
    try:
        engine.load(QUrl.fromLocalFile(str(QML_MAIN)))
        _settle(qt_app, 100)
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        assert isinstance(window, QQuickWindow)
        nav = _visual_item(window.contentItem(), "sidebarNavigation-transcribe")
        nav_icon = _visual_item(window.contentItem(), "navigationIcon-transcribe")
        origin = nav_icon.mapToItem(nav, QPointF(0, 0))
        assert 0 <= origin.x() <= nav.width() - nav_icon.width(), (
            origin.x(), nav.width(), nav_icon.width(), nav_icon.parentItem().width())
        for width, height in WINDOW_SIZES:
            window.setWidth(width)
            window.setHeight(height)
            for route in ROUTES:
                backend.navigate(route)
                _settle(qt_app, 80)
                assert bool(window.property("rightToLeft")) == (locale == "ar")
                screenshot = window.grabWindow()
                assert not screenshot.isNull()
                assert screenshot.save(str(snapshots / f"{route}-{width}x{height}.png"))
                if route in {"transcribe", "settings", "about"}:
                    scroll_name, marker_name = END_MARKERS[route]
                    scroll = _quick_item(window, scroll_name)
                    if _number(scroll, "contentHeight") > scroll.height():
                        _scroll_to_end(qt_app, window, scroll,
                                       _quick_item(window, marker_name))
                if route == "help":
                    backend.navigateHelp("chaves-da-openai-e-do-gemini")
                    _settle(qt_app, 40)
                    scroll = _quick_item(window, "helpArticleScroll")
                    _scroll_to_end(qt_app, window, scroll,
                                   _quick_item(window, "helpArticleEndMarker"))
                if route == "about":
                    popup = window.findChild(QObject, "thirdPartyNoticesPopup")
                    assert popup is not None
                    assert QMetaObject.invokeMethod(popup, "open")
                    _settle(qt_app, 60)
                    assert popup.property("opened")
                    assert window.grabWindow().save(
                        str(snapshots / f"notices-{width}x{height}.png"))
                    QTest.keyClick(window, Qt.Key_Escape)
                    _settle(qt_app, 50)
                    assert not popup.property("opened")
        # Change language while the transcription form is alive; preserve choices.
        backend.navigate("transcribe")
        _settle(qt_app)
        model = window.findChild(QObject, "transcriptionModelSelector")
        language = window.findChild(QObject, "transcriptionLanguageSelector")
        assert model is not None and language is not None
        model.setProperty("currentIndex", 1)
        language.setProperty("currentIndex", 3)
        selected_model = model.property("currentValue")
        selected_language = language.property("currentValue")
        other = "pt-BR" if locale == "en-US" else "en-US"
        assert backend.setInterfaceLanguage(other)
        _settle(qt_app)
        assert model.property("currentValue") == selected_model
        assert language.property("currentValue") == selected_language
        backend.navigate("settings")
        _settle(qt_app)
        key = window.findChild(QObject, "openAiKeyInput")
        assert key is not None
        key.setProperty("text", "fixture-not-a-real-key")
        backend.apiKeyTestFinished.emit("openai", True, "Chave válida")
        assert backend.setInterfaceLanguage(locale)
        _settle(qt_app)
        assert key.property("text") == "fixture-not-a-real-key"
        badge = window.findChild(QObject, "openAiKeyStatus")
        assert badge is not None
        assert badge.property("text") == backend.localizer.text("Chave válida")
        alignment = QQmlExpression(engine.rootContext(), key,
                                   f"Number(effectiveHorizontalAlignment) === {int(Qt.AlignLeft)}")
        aligned, _undefined = alignment.evaluate()
        assert not alignment.hasError(), alignment.error().toString()
        assert aligned is True
        selector = window.findChild(QObject, "interfaceLanguageSelector")
        assert selector is not None and selector.property("currentValue") == locale
        backend.navigate("history")
        _settle(qt_app)
        state_filter = window.findChild(QObject, "historyStateFilter")
        assert state_filter is not None
        state_filter.setProperty("currentIndex", 2)
        assert state_filter.property("currentValue") == "completed"
        assert backend.setInterfaceLanguage(other)
        _settle(qt_app)
        assert state_filter.property("currentValue") == "completed"
        assert backend.setInterfaceLanguage(locale)
        _settle(qt_app)
        assert not warnings, "\n".join(warnings)
        assert settings.value("preferences/interfaceLanguage") == locale
        assert backend._active_job == {}
    finally:
        for root in engine.rootObjects():
            root.close()
        engine.deleteLater()
        _settle(qt_app, 40)
        assert backend.shutdown()
        qt_app.removeTranslator(translator)
        qt_app.setLayoutDirection(Qt.LeftToRight)
    # Persisted locale wins over the English first-run default.
    restored = AppBackend(pipeline=FakePipeline(tmp_path), qsettings=settings)
    try:
        assert restored.interfaceLanguage == locale
    finally:
        assert restored.shutdown()

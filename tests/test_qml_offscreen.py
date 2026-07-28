"""Probe visual Qt reutilizável.

Execute com ``python -m pytest tests/test_qml_offscreen.py -q``. O módulo pula
explicitamente quando PySide6 não está instalado.
"""

# ruff: noqa: E402

from __future__ import annotations

import os
import sys
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Fusion")

PYSIDE_AVAILABLE = find_spec("PySide6") is not None
PYSIDE_SKIP_REASON = (
    "probe QML requer PySide6; instale as dependências do aplicativo"
)
pytestmark = pytest.mark.skipif(
    not PYSIDE_AVAILABLE,
    reason=PYSIDE_SKIP_REASON,
)

if PYSIDE_AVAILABLE:
    from PySide6.QtCore import (
        Property,
        QMetaObject,
        QObject,
        QPointF,
        Qt,
        QUrl,
        Signal,
        Slot,
    )
    from PySide6.QtGui import QFontDatabase, QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtQuick import QQuickItem, QQuickWindow
    from PySide6.QtQuickControls2 import QQuickStyle
    from PySide6.QtTest import QTest
else:
    class _UnavailableQtType:
        pass

    class _UnavailableSignal:
        def emit(self, *_args: Any) -> None:
            return

    def Signal(*_args: Any, **_kwargs: Any) -> _UnavailableSignal:
        return _UnavailableSignal()

    def Property(*_args: Any, **_kwargs: Any) -> Any:
        return lambda function: property(function)

    def Slot(*_args: Any, **_kwargs: Any) -> Any:
        return lambda function: function

    QObject = _UnavailableQtType
    QPointF = _UnavailableQtType
    QUrl = _UnavailableQtType
    Qt = _UnavailableQtType
    QFontDatabase = _UnavailableQtType
    QGuiApplication = _UnavailableQtType
    QQmlApplicationEngine = _UnavailableQtType
    QQuickItem = _UnavailableQtType
    QQuickWindow = _UnavailableQtType
    QQuickStyle = _UnavailableQtType
    QTest = _UnavailableQtType

from sao_francisco.help_system import HelpDocument

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QML_MAIN = PROJECT_ROOT / "sao_francisco" / "qml" / "Main.qml"
HELP_PATH = PROJECT_ROOT / "sao_francisco" / "AJUDA.md"
FONT_DIR = PROJECT_ROOT / "sao_francisco" / "assets" / "fonts"

ROUTES = ("transcribe", "history", "settings", "help", "about")
WINDOW_SIZES = ((1280, 800), (1024, 680))
END_MARKERS = {
    "transcribe": ("transcribePageScroll", "transcribePageEndMarker"),
    "history": ("historyList", "historyEndMarker"),
    "settings": ("settingsPageScroll", "settingsEndMarker"),
    "about": ("aboutPageScroll", "aboutEndMarker"),
}


class ProbeBackend(QObject):
    """Backend determinístico que exercita a interface sem rede ou credenciais."""

    currentRouteChanged = Signal()
    sidebarCollapsedChanged = Signal()
    busyChanged = Signal()
    activeJobStateChanged = Signal()
    canOpenOutputChanged = Signal()
    activeJobChanged = Signal()
    pendingSourcesChanged = Signal()
    outputFolderChanged = Signal()
    historyChanged = Signal()
    settingsChanged = Signal()
    helpAnchorChanged = Signal()
    helpContentChanged = Signal()
    toastRequested = Signal(str)
    apiKeyTestFinished = Signal(str, bool, str)

    def __init__(self, route: str, active_job: dict[str, Any] | None = None) -> None:
        super().__init__()
        self._route = route
        self._sidebar_collapsed = False
        self._help_anchor = "chaves-da-openai-e-do-gemini"
        self._help = HelpDocument.from_path(HELP_PATH)
        self._active_job = active_job or {
            "id": "probe-active",
            "title": "Entrevista extensa para comprovar a composição.mp4",
            "state": "running",
            "detail": "Transcrevendo parte 7 de 24",
            "progress": 0.31,
            "completedParts": 6,
            "totalParts": 24,
            "provenance": "audio_transcription",
        }

    @Property(str, notify=currentRouteChanged)
    def currentRoute(self) -> str:  # noqa: N802 - nome público do contrato QML
        return self._route

    @Property(bool, notify=sidebarCollapsedChanged)
    def sidebarCollapsed(self) -> bool:  # noqa: N802
        return self._sidebar_collapsed

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return False

    @Property(str, constant=True)
    def appVersion(self) -> str:  # noqa: N802
        return "0.1.0-probe"

    @Property(str, constant=True)
    def thirdPartyNoticesMarkdown(self) -> str:  # noqa: N802
        entries = "\n\n".join(
            f"## Componente {index}\n\nLicença e aviso de teste."
            for index in range(1, 13)
        )
        return f"# Avisos de terceiros\n\n{entries}"

    @Property(str, notify=activeJobStateChanged)
    def activeJobState(self) -> str:  # noqa: N802
        return str(self._active_job.get("state") or "")

    @Property(bool, notify=canOpenOutputChanged)
    def canOpenOutput(self) -> bool:  # noqa: N802
        return True

    @Property("QVariantMap", notify=activeJobChanged)
    def activeJob(self) -> dict[str, Any]:  # noqa: N802
        return dict(self._active_job)

    @Property("QVariantList", notify=pendingSourcesChanged)
    def pendingSources(self) -> list[str]:  # noqa: N802
        return []

    @Property(str, notify=outputFolderChanged)
    def outputFolder(self) -> str:  # noqa: N802
        return ""

    @Property("QVariantList", notify=historyChanged)
    def historyItems(self) -> list[dict[str, Any]]:  # noqa: N802
        return self._history_rows()

    @Property("QVariantMap", notify=settingsChanged)
    def settings(self) -> dict[str, Any]:
        return {
            "openAiKeyMasked": "sk-••••••••",
            "geminiKeyMasked": "••••••••",
            "outputFolder": "",
            "notifyOnCompletion": True,
            "resumeInterruptedJobs": True,
        }

    @Property(str, notify=helpAnchorChanged)
    def helpAnchor(self) -> str:  # noqa: N802
        return self._help_anchor

    @Slot(str)
    def navigate(self, route: str) -> None:
        self._route = route
        self.currentRouteChanged.emit()

    @Slot()
    def toggleSidebar(self) -> None:  # noqa: N802
        self._sidebar_collapsed = not self._sidebar_collapsed
        self.sidebarCollapsedChanged.emit()

    @Slot(bool)
    def setSidebarCollapsed(self, collapsed: bool) -> None:  # noqa: N802
        self._sidebar_collapsed = collapsed
        self.sidebarCollapsedChanged.emit()

    @Slot(str)
    def navigateHelp(self, anchor: str) -> None:  # noqa: N802
        self._route = "help"
        self._help_anchor = anchor
        self.currentRouteChanged.emit()
        self.helpAnchorChanged.emit()

    @Slot(str, result="QVariantList")
    def modelsForProvider(self, provider: str) -> list[dict[str, str]]:  # noqa: N802
        if provider == "gemini":
            return [
                {
                    "id": "gemini-probe",
                    "name": "Gemini detalhado",
                    "summary": "Saída estruturada com falantes.",
                }
            ]
        return [
            {
                "id": "gpt-probe",
                "name": "Econômico",
                "summary": "Boa opção inicial.",
            },
            {
                "id": "whisper-probe",
                "name": "Legendas e tempos",
                "summary": "Segmentos precisos.",
            },
        ]

    @Slot("QVariantList")
    def setPendingSources(self, _sources: list[str]) -> None:  # noqa: N802
        return

    @Slot(result=str)
    def chooseOutputFolder(self) -> str:  # noqa: N802
        return ""

    @Slot("QVariantMap")
    def startTranscription(self, _options: dict[str, Any]) -> None:  # noqa: N802
        return

    @Slot()
    def cancelTranscription(self) -> None:  # noqa: N802
        return

    @Slot()
    def openActiveOutput(self) -> None:  # noqa: N802
        return

    @Slot()
    def revealActiveOutput(self) -> None:  # noqa: N802
        return

    @Slot(str)
    def openOutputPath(self, _path: str) -> None:  # noqa: N802
        return

    @Slot(result="QVariantList")
    def history(self) -> list[dict[str, Any]]:
        return self._history_rows()

    @Slot(str)
    def openHistoryOutput(self, _job_id: str) -> None:  # noqa: N802
        return

    @Slot(str)
    def resumeTranscription(self, _job_id: str) -> None:  # noqa: N802
        return

    @Slot(str)
    def showHistoryDetails(self, _job_id: str) -> None:  # noqa: N802
        return

    @Slot(str, result="QVariantList")
    def searchHelp(self, query: str) -> list[dict[str, str]]:  # noqa: N802
        results = self._help.search(query)
        if query.strip():
            return results

        # Conteúdo adicional força rolagem real do índice também em 1280×800.
        return results + [
            {
                "title": f"Tópico de verificação {index + 1}",
                "anchor": f"probe-extra-{index + 1}",
                "excerpt": "Entrada adicional do probe visual.",
            }
            for index in range(8)
        ]

    @Slot(str, result=str)
    def helpSection(self, anchor: str) -> str:  # noqa: N802
        return self._help.section(anchor).markdown

    @Slot(str)
    def openExternalUrl(self, _url: str) -> None:  # noqa: N802
        return

    @Slot("QVariantMap", result=bool)
    def saveSettings(self, _values: dict[str, Any]) -> bool:  # noqa: N802
        return True

    @Slot(str, str, result=bool)
    def testApiKey(self, _provider: str, _candidate: str) -> bool:  # noqa: N802
        return True

    @staticmethod
    def _history_rows() -> list[dict[str, Any]]:
        states = ("completed", "running", "paused", "failed")
        provenances = (
            "existing_captions",
            "author_captions",
            "automatic_captions",
            "audio_transcription",
        )
        return [
            {
                "id": f"job-{index}",
                "title": f"Gravação extensa da sessão número {index + 1}.mp4",
                "createdAtLabel": "27/07/2026 · 19:42",
                "providerLabel": "OpenAI",
                "modelLabel": "Maior precisão",
                "state": states[index % len(states)],
                "progress": 0.5,
                "provenance": provenances[index % len(provenances)],
            }
            for index in range(20)
        ]


@pytest.fixture(scope="module")
def qt_app() -> QGuiApplication:
    QQuickStyle.setStyle("Fusion")
    existing = QGuiApplication.instance()
    app = existing if isinstance(existing, QGuiApplication) else QGuiApplication(sys.argv[:1])

    loaded_families: set[str] = set()
    font_paths = sorted(FONT_DIR.glob("*.ttf"))
    assert font_paths, f"fontes empacotadas não encontradas em {FONT_DIR}"
    for font_path in font_paths:
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        assert font_id >= 0, f"não foi possível registrar {font_path.name}"
        loaded_families.update(QFontDatabase.applicationFontFamilies(font_id))

    assert "Jost" in loaded_families
    assert "Source Sans 3" in loaded_families
    return app


def _settle(app: QGuiApplication, milliseconds: int = 90) -> None:
    QTest.qWait(milliseconds)
    app.processEvents()


def _quick_item(window: QQuickWindow, object_name: str) -> QQuickItem:
    found = window.findChild(QObject, object_name)
    assert found is not None, f"item QML não encontrado: {object_name}"
    assert isinstance(found, QQuickItem), f"{object_name} não é QQuickItem"
    return found


def _number(item: QQuickItem, property_name: str) -> float:
    value = item.property(property_name)
    assert value is not None, f"{item.objectName()}.{property_name} não existe"
    return float(value)


def _scroll_to_end(
    app: QGuiApplication,
    window: QQuickWindow,
    scroll: QQuickItem,
    marker: QQuickItem,
) -> None:
    viewport_height = _number(scroll, "height")
    content_height = _number(scroll, "contentHeight")
    assert content_height > viewport_height, (
        f"{scroll.objectName()} não transbordou: "
        f"{content_height} <= {viewport_height}"
    )

    origin_y = _number(scroll, "originY") if scroll.property("originY") is not None else 0.0
    maximum = max(0.0, content_height - viewport_height + origin_y)
    scroll.setProperty("contentY", origin_y)
    scroll.forceActiveFocus()
    QTest.keyClick(window, Qt.Key.Key_PageDown)
    _settle(app)

    current_y = _number(scroll, "contentY")
    assert current_y > origin_y

    QTest.keyClick(window, Qt.Key.Key_End)
    _settle(app)
    current_y = _number(scroll, "contentY")
    assert current_y >= maximum - 2.0

    marker_position = marker.mapToItem(scroll, QPointF(0, 0))
    marker_top = marker_position.y()
    marker_bottom = marker_top + max(1.0, marker.height())
    assert marker_top <= viewport_height + 2.0
    assert marker_bottom >= -2.0


def _verify_help(
    app: QGuiApplication,
    window: QQuickWindow,
) -> None:
    topic_list = _quick_item(window, "helpTopicList")
    topic_bar = _quick_item(window, "helpTopicScrollBar")
    article_scroll = _quick_item(window, "helpArticleScroll")
    article_bar = _quick_item(window, "helpArticleScrollBar")
    article_marker = _quick_item(window, "helpArticleEndMarker")

    assert topic_list is not article_scroll
    assert topic_bar is not article_bar
    assert bool(topic_bar.property("interactive"))
    assert bool(article_bar.property("interactive"))

    topic_viewport = _number(topic_list, "height")
    topic_content = _number(topic_list, "contentHeight")
    assert topic_content > topic_viewport

    article_scroll.setProperty("contentY", 0.0)
    topic_list.setProperty("contentY", 0.0)
    topic_list.forceActiveFocus()
    QTest.keyClick(window, Qt.Key.Key_PageDown)
    _settle(app)
    assert _number(topic_list, "contentY") > 0
    assert _number(article_scroll, "contentY") == pytest.approx(0.0, abs=1.0)

    topic_position_after_index_scroll = _number(topic_list, "contentY")
    article_scroll.forceActiveFocus()
    QTest.keyClick(window, Qt.Key.Key_PageDown)
    _settle(app)
    assert _number(article_scroll, "contentY") > 0
    assert _number(topic_list, "contentY") == pytest.approx(
        topic_position_after_index_scroll,
        abs=1.0,
    )

    QTest.keyClick(window, Qt.Key.Key_End)
    _settle(app)
    article_maximum = max(
        0.0,
        _number(article_scroll, "contentHeight") - _number(article_scroll, "height"),
    )
    assert _number(article_scroll, "contentY") >= article_maximum - 2.0

    marker_position = article_marker.mapToItem(article_scroll, QPointF(0, 0))
    assert marker_position.y() <= _number(article_scroll, "height") + 2.0
    assert marker_position.y() + max(1.0, article_marker.height()) >= -2.0


@pytest.mark.parametrize(("width", "height"), WINDOW_SIZES)
@pytest.mark.parametrize("route", ROUTES)
def test_all_qml_routes_render_and_reach_the_end(
    qt_app: QGuiApplication,
    tmp_path: Path,
    route: str,
    width: int,
    height: int,
) -> None:
    backend = ProbeBackend(route)
    engine = QQmlApplicationEngine()
    qml_warnings: list[str] = []
    engine.warnings.connect(
        lambda messages: qml_warnings.extend(message.toString() for message in messages)
    )
    engine.rootContext().setContextProperty("appBackend", backend)

    try:
        engine.load(QUrl.fromLocalFile(str(QML_MAIN)))
        _settle(qt_app, 180)
        roots = engine.rootObjects()
        assert roots, "Main.qml não criou a janela:\n" + "\n".join(qml_warnings)
        window = roots[0]
        assert isinstance(window, QQuickWindow)

        window.setWidth(width)
        window.setHeight(height)
        window.show()
        _settle(qt_app, 160)

        assert window.width() == width
        assert window.height() == height
        assert not qml_warnings, "erros/warnings QML:\n" + "\n".join(qml_warnings)

        screenshot = window.grabWindow()
        assert not screenshot.isNull(), f"captura vazia em {route} {width}×{height}"
        screenshot_path = tmp_path / f"{route}-{width}x{height}.png"
        assert screenshot.save(str(screenshot_path))

        if route == "help":
            _verify_help(qt_app, window)
        else:
            scroll_name, marker_name = END_MARKERS[route]
            _scroll_to_end(
                qt_app,
                window,
                _quick_item(window, scroll_name),
                _quick_item(window, marker_name),
            )
    finally:
        for root in engine.rootObjects():
            if isinstance(root, QQuickWindow):
                root.close()
        engine.deleteLater()
        _settle(qt_app, 40)


def test_improve_with_ai_starts_off_and_accepts_keyboard(
    qt_app: QGuiApplication,
) -> None:
    backend = ProbeBackend("transcribe")
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appBackend", backend)

    try:
        engine.load(QUrl.fromLocalFile(str(QML_MAIN)))
        _settle(qt_app, 180)
        window = engine.rootObjects()[0]
        assert isinstance(window, QQuickWindow)
        window.setWidth(1024)
        window.setHeight(680)
        window.show()
        _settle(qt_app)

        checkbox = _quick_item(window, "improveWithAiCheck")
        assert checkbox.property("checked") is False
        assert checkbox.property("enabled") is True
        checkbox.forceActiveFocus()
        QTest.keyClick(window, Qt.Key.Key_Space)
        _settle(qt_app)
        assert checkbox.property("checked") is True
    finally:
        for root in engine.rootObjects():
            if isinstance(root, QQuickWindow):
                root.close()
        engine.deleteLater()
        _settle(qt_app, 40)


@pytest.mark.parametrize("variant", ("completed", "improvement_failed"))
def test_transcribe_result_states_render_without_clipping(
    qt_app: QGuiApplication,
    tmp_path: Path,
    variant: str,
) -> None:
    if variant == "completed":
        active_job = {
            "id": "probe-completed",
            "title": "Entrevista sobre nomes, números e memória coletiva.mp4",
            "state": "completed",
            "stage": "completed",
            "detail": "Concluída; os arquivos estão prontos.",
            "progress": 1.0,
            "completedParts": 3,
            "totalParts": 3,
            "provenance": "audio_transcription",
            "costLabel": "Custo estimado: cerca de US$ 0,08",
            "usageLabel": "Uso informado: 18.240 tokens",
            "outputGroups": {
                "improved": [
                    str(tmp_path / "Entrevista — texto melhorado.docx"),
                    str(tmp_path / "Entrevista — texto melhorado.txt"),
                ],
                "original": [
                    str(tmp_path / "Entrevista — transcrição.docx"),
                    str(tmp_path / "Entrevista — transcrição.txt"),
                ],
                "captions": [str(tmp_path / "Entrevista.srt")],
            },
        }
    else:
        active_job = {
            "id": "probe-failed",
            "title": "Entrevista extensa.mp4",
            "state": "failed",
            "stage": "improving",
            "detail": (
                "Não foi possível melhorar o texto. A transcrição original está "
                "preservada e os arquivos finais ainda não foram criados."
            ),
            "progress": 0.78,
            "completedParts": 1,
            "totalParts": 3,
            "provenance": "audio_transcription",
            "costLabel": "Custo estimado: cerca de US$ 0,04",
            "usageLabel": "Uso informado: 9.120 tokens",
            "outputGroups": {},
        }

    backend = ProbeBackend("transcribe", active_job)
    engine = QQmlApplicationEngine()
    warnings: list[str] = []
    engine.warnings.connect(
        lambda messages: warnings.extend(message.toString() for message in messages)
    )
    engine.rootContext().setContextProperty("appBackend", backend)

    try:
        engine.load(QUrl.fromLocalFile(str(QML_MAIN)))
        _settle(qt_app, 180)
        window = engine.rootObjects()[0]
        assert isinstance(window, QQuickWindow)
        window.setWidth(1024)
        window.setHeight(680)
        window.show()
        _settle(qt_app, 120)
        assert not warnings

        scroll = _quick_item(window, "transcribePageScroll")
        marker = _quick_item(window, "transcribePageEndMarker")
        _scroll_to_end(qt_app, window, scroll, marker)
        screenshot = window.grabWindow()
        assert screenshot.save(str(tmp_path / f"transcribe-{variant}.png"))
    finally:
        for root in engine.rootObjects():
            if isinstance(root, QQuickWindow):
                root.close()
        engine.deleteLater()
        _settle(qt_app, 40)


def test_third_party_notices_open_scroll_and_close_inside_the_app(
    qt_app: QGuiApplication,
    tmp_path: Path,
) -> None:
    backend = ProbeBackend("about")
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appBackend", backend)

    try:
        engine.load(QUrl.fromLocalFile(str(QML_MAIN)))
        _settle(qt_app, 180)
        window = engine.rootObjects()[0]
        assert isinstance(window, QQuickWindow)
        window.setWidth(1024)
        window.setHeight(680)
        window.show()
        _settle(qt_app, 120)

        popup = window.findChild(QObject, "thirdPartyNoticesPopup")
        assert popup is not None
        assert QMetaObject.invokeMethod(popup, "open")
        _settle(qt_app, 120)
        assert bool(popup.property("opened"))

        scroll = _quick_item(window, "thirdPartyNoticesScroll")
        assert _number(scroll, "contentHeight") > _number(scroll, "height")
        scroll.forceActiveFocus()
        QTest.keyClick(window, Qt.Key.Key_End)
        _settle(qt_app)
        assert _number(scroll, "contentY") > 0

        assert window.findChild(QObject, "thirdPartyNoticesCloseIcon") is not None
        assert window.findChild(QObject, "thirdPartyNoticesCloseButton") is not None
        screenshot = window.grabWindow()
        assert screenshot.save(str(tmp_path / "third-party-notices.png"))

        QTest.keyClick(window, Qt.Key.Key_Escape)
        _settle(qt_app)
        assert not bool(popup.property("opened"))
    finally:
        for root in engine.rootObjects():
            if isinstance(root, QQuickWindow):
                root.close()
        engine.deleteLater()
        _settle(qt_app, 40)

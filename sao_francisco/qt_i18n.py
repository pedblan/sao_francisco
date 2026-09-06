"""Qt adapter for the offline product-copy catalog."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QTranslator

from .i18n import Localizer


class ProductTranslator(QTranslator):
    def __init__(
        self, localizer: Callable[[], Localizer], parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._localizer = localizer

    def isEmpty(self) -> bool:  # noqa: N802
        return False

    def translate(
        self,
        context: str,
        sourceText: str,  # noqa: N803
        disambiguation: str | None = None,
        n: int = -1,
    ) -> str:
        # Returning an empty Python string suppresses native Qt labels instead
        # of falling through like a null QString. Preserve unrelated Qt copy.
        return self._localizer().text(sourceText) if context == "App" else sourceText

from __future__ import annotations

from aqt.qt import Qt, QWidget

from ..consts import consts
from ..vendor.ankiutils.gui import dialog


class Dialog(dialog.Dialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        flags: Qt.WindowType = Qt.WindowType.Dialog,
        subtitle: str = "",
    ) -> None:
        self.subtitle = subtitle
        super().__init__(consts=consts, parent=parent, flags=flags, subtitle=subtitle)

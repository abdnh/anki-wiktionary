from __future__ import annotations

from aqt.qt import QWidget

from .sveltekit_web import SveltekitWebDialog


class HelpDialog(SveltekitWebDialog):
    key = "help"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(path="help", parent=parent, subtitle="Help")

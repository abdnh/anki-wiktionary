from __future__ import annotations

from aqt.qt import QWidget

from ..backend.server import get_server
from ..consts import consts
from ..log import logger
from ..vendor.ankiutils.gui import sveltekit_web


class SveltekitWebDialog(sveltekit_web.SveltekitWebDialog):
    def __init__(self, path: str, parent: QWidget | None = None, subtitle: str = ""):
        self.path = path
        super().__init__(
            consts=consts,
            logger=logger,
            server=get_server(),
            path=path,
            parent=parent,
            subtitle=subtitle,
        )

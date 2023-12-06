from typing import Optional

import ankiutils.gui.dialog
from aqt.qt import *


class Dialog(ankiutils.gui.dialog.Dialog):
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Dialog,
    ) -> None:
        super().__init__(__name__, parent, flags)

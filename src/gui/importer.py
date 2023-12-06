from __future__ import annotations

import os
import re
import sys
import traceback
from concurrent.futures import Future
from typing import TYPE_CHECKING

from aqt import qtmajor
from aqt.main import AnkiQt
from aqt.qt import QKeySequence, qconnect
from aqt.utils import getFile, openLink, showWarning, tooltip

from ..consts import consts
from ..fetcher import WiktionaryFetcher
from ..gui.dialog import Dialog

if TYPE_CHECKING or qtmajor > 5:
    from ..forms.importer_qt6 import Ui_Dialog
else:
    from ..forms.importer_qt5 import Ui_Dialog  # type: ignore


class ImportDictionaryDialog(Dialog):
    key = "importer"

    def __init__(
        self,
        mw: AnkiQt,
    ):
        self.mw = mw
        super().__init__(mw)
        self.errors: list[str] = []

    def setup_ui(self) -> None:
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        qconnect(
            self.form.chooseFileButton.clicked,
            self.on_choose_file,
        )
        qconnect(self.form.addButton.clicked, self.on_add)
        self.form.addButton.setShortcut(QKeySequence("Ctrl+Return"))
        self.form.description.setText(
            """
Here you can import a new dictionary downloaded from <a href="https://kaikki.org/dictionary/">the dictionary list at kaikki.org</a>.<br>
After finding your language link in the list and opening it, you'll find an option<br>
at the bottom of the page to download a JSON file (which has a name like "kaikki.org-dictionary-Russian.json")<br>
containing all word senses that you can import to Anki here.<br>
The imported dictionary will be made available for use in the add-on's main dialog."""
        )
        qconnect(
            self.form.description.linkActivated,
            lambda link: openLink(link),  # pylint: disable=unnecessary-lambda
        )
        super().setup_ui()

    def on_choose_file(self) -> None:
        filename = getFile(
            self,
            title=consts.name,
            cb=None,
            key=consts.name,
        )
        if not filename:
            return
        filename = str(filename)
        self.form.filenameLabel.setText(filename)
        name_match = re.search(r"kaikki.org-dictionary-(.*?)\.", filename)
        if name_match:
            name = name_match.group(1)
        else:
            name, _ = os.path.splitext(os.path.basename(filename))
        self.form.dictionaryNameLineEdit.setText(name)

    def on_add(self) -> None:
        want_cancel = False

        def on_progress(count: int) -> bool:
            def update() -> None:
                self.mw.progress.update(f"Imported {count} words...")
                nonlocal want_cancel
                want_cancel = self.mw.progress.want_cancel()

            self.mw.taskman.run_on_main(update)
            return not want_cancel

        def on_error(word: str, exc: Exception) -> None:
            self.errors.append(f'failed to write file of word "{word}": {str(exc)}')

        def on_done(future: Future) -> None:
            self.mw.progress.finish()
            try:
                count = future.result()
            except Exception as exc:
                traceback.print_exception(None, exc, exc.__traceback__, file=sys.stdout)
                showWarning(str(exc), parent=self, title=consts.name)
                return
            tooltip(f"Successfully imported {count} words", parent=self.mw)
            self.accept()

        filename = self.form.filenameLabel.text()
        name = self.form.dictionaryNameLineEdit.text().strip()
        if not name or not filename:
            showWarning("Filename and dictionary name fields cannot be empty")
            return
        self.mw.progress.start(label="Starting importing...", parent=self)
        self.mw.progress.set_title(f"{consts.name} - Importing a dictionary")
        self.mw.taskman.run_in_background(
            lambda: WiktionaryFetcher.import_kaikki_dict(
                filename,
                name,
                on_progress=on_progress,
                on_error=on_error,
                base_dir=consts.dicts_dir,
            ),
            on_done=on_done,
        )

from concurrent.futures import Future
import re
from typing import List

from aqt.qt import *
from aqt import qtmajor
from aqt.main import AnkiQt
from aqt.utils import showWarning, getFile, tooltip, openLink


if qtmajor > 5:
    from .import_dictionary_qt6 import Ui_Dialog
else:
    from .import_dictionary_qt5 import Ui_Dialog

from . import consts
from .wiktionary_fetcher import WiktionaryFetcher


class ImportDictionaryDialog(QDialog):
    def __init__(
        self,
        mw: AnkiQt,
    ):
        super().__init__(mw)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.mw = mw
        self.errors: List[str] = []
        self.setup_ui()

    def setup_ui(self) -> None:
        qconnect(
            self.form.chooseFileButton.clicked,
            lambda: getFile(
                self,
                title=consts.ADDON_NAME,
                cb=self.on_choose_file,
                key=consts.ADDON_NAME,
            ),
        )
        qconnect(self.form.addButton.clicked, self.on_add)
        self.form.description.setText(
            """
Here you can import a new dictionary downloaded from <a href="https://kaikki.org/dictionary/">the dictionary list at kaikki.org</a>.<br>
After finding your language link in the list and opening it, you'll find an option<br>
at the bottom of the page to download a JSON file (which has a name like "kaikki.org-dictionary-Russian.json")<br>
containing all word senses that you can import to Anki here.<br>
The imported dictionary will be made available for use in the add-on's main dialog."""
        )
        qconnect(self.form.description.linkActivated, lambda link: openLink(link))

    def on_choose_file(self, filename: str) -> None:
        self.form.filenameLineEdit.setText(filename)
        name_match = re.search(r"kaikki.org-dictionary-(.*?)\.", filename)
        if name_match:
            self.form.dictionaryNameLineEdit.setText(name_match.group(1))

    def on_add(self) -> None:
        def on_progress(count: int):
            self.mw.taskman.run_on_main(
                lambda: self.mw.progress.update(f"Imported {count} words...")
            )

        def on_error(word: str, exc: Exception) -> None:
            self.errors.append(f'failed to write file of word "{word}": {str(exc)}')

        def on_done(future: Future) -> None:
            self.mw.progress.finish()
            try:
                count = future.result()
            except Exception as exc:
                showWarning(str(exc), parent=self, title=consts.ADDON_NAME)
                return
            tooltip(f"Successfully imported {count} words", parent=self.mw)
            self.accept()

        filename = self.form.filenameLineEdit.text()
        name = self.form.dictionaryNameLineEdit.text().strip()
        if not name or not filename:
            showWarning("Filename and dictionary name fields cannot be empty")
            return
        self.mw.progress.start(label="Starting importing...", parent=self)
        self.mw.progress.set_title(f"{consts.ADDON_NAME} - Importing a dictionary")
        # TODO: handle exceptions
        self.mw.taskman.run_in_background(
            lambda: WiktionaryFetcher.dump_kaikki_dict(
                filename, name, on_progress=on_progress, on_error=on_error
            ),
            on_done=on_done,
        )

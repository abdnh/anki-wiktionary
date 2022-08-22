import re
from concurrent.futures import Future
from typing import List

from aqt import qtmajor
from aqt.main import AnkiQt
from aqt.qt import QDialog, qconnect
from aqt.utils import getFile, openLink, showWarning, tooltip

from . import consts

from .dictionaries import dictionary_classes

if qtmajor > 5:
    from .forms.import_dictionary_qt6 import Ui_Dialog
else:
    from .forms.import_dictionary_qt5 import Ui_Dialog  # type: ignore


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
            self.on_choose_file,
        )
        qconnect(self.form.addButton.clicked, self.on_add)
        qconnect(
            self.form.description.linkActivated,
            lambda link: openLink(link),  # pylint: disable=unnecessary-lambda
        )
        self.form.dictionaryComboBox.addItems([d.name for d in dictionary_classes])
        qconnect(self.form.dictionaryComboBox.currentIndexChanged, self.on_dict_changed)
        self.on_dict_changed(0)

    def on_dict_changed(self, index: int) -> None:
        desc = dictionary_classes[index].desc
        self.form.description.setText(desc)

    def on_choose_file(self) -> None:
        dictionary = dictionary_classes[self.form.dictionaryComboBox.currentIndex()]
        filename = getFile(
            self,
            title=consts.ADDON_NAME,
            cb=None,
            filter=f"*.{dictionary.ext}",
            key=consts.ADDON_NAME,
        )
        if not filename:
            return
        filename = str(filename)
        self.form.filenameLabel.setText(filename)
        name_match = re.search(r"kaikki.org-dictionary-(.*?)\.", filename)
        if name_match:
            self.form.dictionaryNameLineEdit.setText(name_match.group(1))

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
                showWarning(str(exc), parent=self, title=consts.ADDON_NAME)
                return
            if count is not None:
                tooltip(f"Successfully imported {count} words", parent=self.mw)
            else:
                tooltip("Successfully imported dictionary", parent=self.mw)
            self.accept()

        filename = self.form.filenameLabel.text()
        name = self.form.dictionaryNameLineEdit.text().strip()
        if not name or not filename:
            showWarning("Filename and dictionary name fields cannot be empty")
            return
        self.mw.progress.start(label="Starting importing...", parent=self)
        self.mw.progress.set_title(f"{consts.ADDON_NAME} - Importing a dictionary")
        dictionary = dictionary_classes[self.form.dictionaryComboBox.currentIndex()]
        dictionary_root_folder = consts.USER_FILES / dictionary.name
        dictionary_root_folder.mkdir(exist_ok=True)
        output_folder = dictionary_root_folder / name
        self.mw.taskman.run_in_background(
            lambda: dictionary.build_dict(
                filename, output_folder, on_progress, on_error
            ),
            on_done=on_done,
        )

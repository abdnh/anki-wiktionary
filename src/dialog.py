from typing import List, Optional, Tuple

from aqt.qt import *
from aqt import qtmajor
from aqt.main import AnkiQt
from aqt.utils import showWarning
from anki.notes import Note
from aqt.operations import QueryOp

if qtmajor > 5:
    from .form_qt6 import Ui_Dialog
else:
    from .form_qt5 import Ui_Dialog

# from .consts import *
from . import consts
from .wiktionary_fetcher import WiktionaryFetcher, WordNotFoundError

PROGRESS_LABEL = "Updated {count} out of {total} note(s)"


def get_available_dicts() -> List[str]:
    return [p.name for p in consts.USER_FILES.iterdir() if p.is_dir()]


class WiktionaryFetcherDialog(QDialog):
    def __init__(
        self,
        mw: AnkiQt,
        parent,
        notes: List[Note],
    ):
        super().__init__(parent)
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        self.mw = mw
        self.notes = notes
        self.combos = [
            self.form.wordFieldComboBox,
            self.form.definitionFieldComboBox,
            self.form.exampleFieldComboBox,
            self.form.genderFieldComboBox,
            self.form.POSFieldComboBox,
        ]
        self.setWindowTitle(consts.ADDON_NAME)
        self.form.icon.setPixmap(
            QPixmap(os.path.join(consts.ICONS_DIR, "enwiktionary-1.5x.png"))
        )
        self.form.dictionaryComboBox.addItems(get_available_dicts())
        self.downloader: Optional[WiktionaryFetcher] = None
        qconnect(self.form.addButton.clicked, self.on_add)

    def exec(self) -> int:
        if self._fill_fields():
            return super().exec()
        else:
            return QDialog.DialogCode.Rejected

    def _fill_fields(self) -> int:
        mids = set(note.mid for note in self.notes)
        if len(mids) > 1:
            showWarning(
                "Please select notes from only one notetype.",
                parent=self,
                title=consts.ADDON_NAME,
            )
            return 0
        self.field_names = ["None"] + self.notes[0].keys()
        for i, combo in enumerate(self.combos):
            combo.addItems(self.field_names)
            selected = 0
            if len(self.field_names) - 1 > i:
                selected = i + 1
            combo.setCurrentIndex(selected)
            qconnect(
                combo.currentIndexChanged,
                lambda field_index, combo_index=i: self.on_selected_field_changed(
                    combo_index, field_index
                ),
            )
        return 1

    def on_selected_field_changed(self, combo_index, field_index):
        if field_index == 0:
            return
        for i, combo in enumerate(self.combos):
            if i != combo_index and combo.currentIndex() == field_index:
                combo.setCurrentIndex(0)

    def on_add(self):
        if self.form.wordFieldComboBox.currentIndex() == 0:
            showWarning("No word field selected.", parent=self, title=consts.ADDON_NAME)
            return
        if self.form.dictionaryComboBox.currentIndex() == -1:
            showWarning(
                "No dictionary is available. Please use <b>Tools > Wiktionary > Import a dictionary</b>.",
                textFormat="rich",
            )
            return
        dictionary = self.form.dictionaryComboBox.currentText()
        self.downloader = WiktionaryFetcher(dictionary)
        word_field = self.form.wordFieldComboBox.currentText()
        definition_field_i = self.form.definitionFieldComboBox.currentIndex()
        example_field_i = self.form.exampleFieldComboBox.currentIndex()
        gender_field_i = self.form.genderFieldComboBox.currentIndex()
        pos_field_i = self.form.POSFieldComboBox.currentIndex()
        field_tuples = (
            (definition_field_i, self._get_definitions),
            (example_field_i, self._get_examples),
            (gender_field_i, self._get_gender),
            (pos_field_i, self._get_part_of_speech),
        )

        def on_success(ret):
            self.accept()

        def on_failure(exc):
            self.mw.progress.finish()
            showWarning(str(exc), parent=self, title=consts.ADDON_NAME)
            self.accept()

        op = QueryOp(
            parent=self,
            op=lambda col: self._fill_notes(
                word_field,
                field_tuples,
            ),
            success=on_success,
        )
        op.failure(on_failure)
        op.run_in_background()
        self.mw.progress.start(
            max=len(self.notes),
            label=PROGRESS_LABEL.format(count=0, total=len(self.notes)),
            parent=self,
            immediate=True,
        )
        self.mw.progress.set_title(consts.ADDON_NAME)

    def _fill_notes(
        self,
        word_field,
        field_tuples: Tuple[Tuple[int, Callable[[str], str]]],
    ):
        self.errors = []
        self.updated_notes = []
        for note in self.notes:
            word = note[word_field]
            try:
                need_updating = False
                for field_tuple in field_tuples:
                    if not field_tuple[0]:
                        continue
                    contents = field_tuple[1](word)
                    note[self.field_names[field_tuple[0]]] = contents
                    need_updating = True
            except WordNotFoundError as exc:
                self.errors.append(str(exc))
            finally:
                if need_updating:
                    self.updated_notes.append(note)
                    self.mw.taskman.run_on_main(
                        lambda: self.mw.progress.update(
                            label=PROGRESS_LABEL.format(
                                count=len(self.updated_notes), total=len(self.notes)
                            ),
                            value=len(self.updated_notes),
                            max=len(self.notes),
                        )
                    )
        self.mw.taskman.run_on_main(lambda: self.mw.progress.finish())

    def _get_definitions(self, word: str) -> str:
        field_contents = []
        defs = self.downloader.get_senses(word)
        for i, definition in enumerate(defs):
            field_contents.append(f"{i}. {definition}")
        return "<br>".join(field_contents)

    def _get_examples(self, word: str) -> str:
        field_contents = []
        examples = self.downloader.get_examples(word)
        for example in examples:
            field_contents.append(example)
        return "<br>".join(field_contents)

    def _get_gender(self, word: str) -> str:
        return self.downloader.get_gender(word)

    def _get_part_of_speech(self, word: str) -> str:
        return self.downloader.get_part_of_speech(word)

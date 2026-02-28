from aqt import mw
from aqt.qt import QAction, QMenu, qconnect
from aqt.utils import showText

from .consts import consts
from .gui.help import HelpDialog
from .gui.importer import ImportDictionaryDialog


def on_help() -> None:
    dialog = HelpDialog()
    dialog.open()


def on_import_dictionary() -> None:
    dialog = ImportDictionaryDialog(mw)
    dialog.exec()
    if dialog.errors:
        showText(
            "The following errors happened during the process:\n" + "\n".join(dialog.errors),
            copyBtn=True,
        )


def add_menu() -> None:
    menu = QMenu(consts.name, mw)
    import_action = QAction("Import a dictionary", menu)
    qconnect(import_action.triggered, on_import_dictionary)
    menu.addAction(import_action)
    help_action = QAction("Help", menu)
    qconnect(help_action.triggered, on_help)
    menu.addAction(help_action)
    mw.form.menuTools.addMenu(menu)

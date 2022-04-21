from typing import List

from aqt.gui_hooks import (
    browser_menus_did_init,
    editor_did_init_buttons,
)
import aqt
from aqt.qt import *
from aqt.browser.browser import Browser
from aqt.editor import Editor
from aqt.utils import showText, tooltip, showWarning
from aqt.operations import CollectionOp

from .consts import *
from .dialog import WiktionaryFetcherDialog
from .wiktionary_fetcher import WiktionaryFetcher

downloader = WiktionaryFetcher()


def on_bulk_updated_notes(browser: Browser, errors: List[str], updated_count: int):
    if updated_count:
        tooltip(f"Updated {updated_count} note(s).", period=5000, parent=browser)
    if len(errors) == 1:
        showWarning(errors[0], parent=browser, title=ADDON_NAME)
    elif errors:
        msg = ""
        msg += " The following issues happened during the process:\n"
        msg += "\n".join(errors)
        showText(msg, parent=browser, title=ADDON_NAME)


def on_browser_action_triggered(browser: Browser) -> None:
    notes = [browser.mw.col.get_note(nid) for nid in browser.selected_notes()]
    dialog = WiktionaryFetcherDialog(browser.mw, browser, downloader, notes)
    if dialog.exec():
        updated_notes = dialog.updated_notes
        errors = dialog.errors
        CollectionOp(
            parent=browser,
            op=lambda col: col.update_notes(updated_notes),
        ).success(
            lambda out: on_bulk_updated_notes(browser, errors, len(updated_notes)),
        ).run_in_background()


def on_browser_menus_did_init(browser: Browser):
    config = aqt.mw.addonManager.getConfig(__name__)
    shortcut = config["browser_shortcut"]
    a = QAction("Bulk-define from Wiktionary", browser)
    a.setShortcut(shortcut)
    qconnect(a.triggered, lambda: on_browser_action_triggered(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)


def on_editor_button_clicked(editor: Editor) -> None:
    dialog = WiktionaryFetcherDialog(
        editor.mw, editor.parentWindow, downloader, [editor.note]
    )
    if dialog.exec():
        if dialog.errors:
            showWarning(
                "\n".join(dialog.errors),
                parent=editor.parentWindow,
                title=ADDON_NAME,
            )
        editor.loadNoteKeepingFocus()


def on_editor_did_init_buttons(buttons: List[str], editor: Editor):
    config = aqt.mw.addonManager.getConfig(__name__)
    shortcut = config["editor_shortcut"]
    button = editor.addButton(
        icon=os.path.join(ICONS_DIR, "en.ico"),
        cmd="wiktionary",
        tip=f"{ADDON_NAME} ({shortcut})" if shortcut else ADDON_NAME,
        func=on_editor_button_clicked,
        keys=shortcut,
    )
    buttons.append(button)


browser_menus_did_init.append(on_browser_menus_did_init)
editor_did_init_buttons.append(on_editor_did_init_buttons)

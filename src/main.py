from __future__ import annotations

import os

from anki.collection import Collection, OpChanges
from aqt import mw
from aqt.browser.browser import Browser
from aqt.editor import Editor
from aqt.gui_hooks import browser_menus_did_init, editor_did_init_buttons
from aqt.operations import CollectionOp
from aqt.qt import QAction, QKeySequence, qconnect
from aqt.utils import showText, showWarning, tooltip

from .patches import patch_certifi

patch_certifi()

# ruff: noqa: E402
from .backend.server import init_server
from .consts import consts
from .errors import setup_error_handler
from .gui.main import WiktionaryFetcherDialog
from .menu import add_menu
from .migration import migrate_legacy_dicts


def on_bulk_updated_notes(browser: Browser, errors: list[str], updated_count: int) -> None:
    if updated_count:
        tooltip(f"Updated {updated_count} note(s).", period=5000, parent=browser)
    if len(errors) == 1:
        showWarning(errors[0], parent=browser, title=consts.name)
    elif errors:
        msg = ""
        msg += " The following issues happened during the process:\n"
        msg += "\n".join(errors)
        showText(msg, parent=browser, title=consts.name, copyBtn=True)


def on_browser_action_triggered(browser: Browser) -> None:
    notes = [browser.mw.col.get_note(nid) for nid in browser.selected_notes()]
    dialog = WiktionaryFetcherDialog(browser.mw, browser, notes)
    if dialog.exec():
        updated_notes = dialog.updated_notes
        errors = dialog.errors

        def op(col: Collection) -> OpChanges:
            pos = col.add_custom_undo_entry(f"Fill {len(updated_notes)} notes with data from Wiktionary")
            col.update_notes(updated_notes)
            return col.merge_undo_entries(pos)

        CollectionOp(
            parent=browser,
            op=op,
        ).success(
            lambda out: on_bulk_updated_notes(browser, errors, len(updated_notes)),
        ).run_in_background()


def on_browser_menus_did_init(browser: Browser) -> None:
    config = mw.addonManager.getConfig(__name__)
    shortcut = config["browser_shortcut"]
    action = QAction("Bulk-define from Wiktionary", browser)
    action.setShortcut(shortcut)
    qconnect(action.triggered, lambda: on_browser_action_triggered(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(action)


def on_editor_button_clicked(editor: Editor) -> None:
    dialog = WiktionaryFetcherDialog(editor.mw, editor.parentWindow, [editor.note])
    if dialog.exec():
        if dialog.errors:
            showWarning(
                "\n".join(dialog.errors),
                parent=editor.parentWindow,
                title=consts.name,
            )
        editor.loadNoteKeepingFocus()


def on_editor_did_init_buttons(buttons: list[str], editor: Editor) -> None:
    config = mw.addonManager.getConfig(__name__)
    shortcut = QKeySequence(config["editor_shortcut"]).toString(QKeySequence.SequenceFormat.NativeText)
    button = editor.addButton(
        icon=os.path.join(consts.icons_dir, "en.ico"),
        cmd="wiktionary",
        tip=f"{consts.name} ({shortcut})" if shortcut else consts.name,
        func=on_editor_button_clicked,
        keys=shortcut,
        disables=False,
    )
    buttons.append(button)


def init() -> None:
    setup_error_handler()
    browser_menus_did_init.append(on_browser_menus_did_init)
    editor_did_init_buttons.append(on_editor_did_init_buttons)
    migrate_legacy_dicts()
    add_menu()
    init_server()

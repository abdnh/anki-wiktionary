from __future__ import annotations

import atexit
import logging
from typing import Callable

from anki.hooks import wrap
from aqt import gui_hooks, mw
from aqt.qt import QWidget

from .config import config
from .consts import consts
from .log import logger
from .vendor.ankiutils import errors
from .vendor.ankiutils.errors import ErrorReportingArgs, LogsUpload
from .vendor.ankiutils.gui.errors import upload_logs_and_notify_user as upload_logs_and_notify_user_base

REGISTERED_ERROR_HANDLER = False
ARGS = ErrorReportingArgs(consts=consts, config=config, logger=logger)


def _on_profile_did_open(on_done: Callable | None = None) -> None:
    global REGISTERED_ERROR_HANDLER

    if not REGISTERED_ERROR_HANDLER:
        errors.setup_error_handler(ARGS)
        REGISTERED_ERROR_HANDLER = True
    if on_done:
        on_done()


def _before_exit() -> None:
    # Fix 'RuntimeError: wrapped C/C++ object of type ErrorHandler has been deleted'
    # on shutdown
    atexit.unregister(logging.shutdown)
    logging.shutdown()


def setup_error_handler(on_done: Callable | None = None) -> None:
    gui_hooks.profile_did_open.append(lambda: _on_profile_did_open(on_done))
    mw.cleanupAndExit = wrap(mw.cleanupAndExit, _before_exit, "before")  # type: ignore


def report_exception_and_upload_logs(
    parent: QWidget, exception: BaseException, on_success: Callable[[str | None], None] | None = None
) -> None:
    errors.report_exception_and_upload_logs_op(
        parent=parent, exception=exception, args=ARGS, on_success=on_success
    ).run_in_background()


def upload_logs(parent: QWidget, on_success: Callable[[LogsUpload | None], None] | None = None) -> None:
    errors.upload_logs_op(parent=parent, args=ARGS, on_success=on_success).run_in_background()


def upload_logs_and_notify_user(parent: QWidget) -> None:
    upload_logs_and_notify_user_base(parent=parent, args=ARGS)

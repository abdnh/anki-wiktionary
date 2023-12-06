from anki.collection import Collection
from anki.utils import pointVersion
from aqt import mw
from aqt.operations import QueryOp
from aqt.utils import tooltip

from .consts import consts
from .fetcher import WiktionaryFetcher
from .utils import get_legacy_dict_dirs


def migrate_legacy_dicts() -> None:
    legacy_dicts = get_legacy_dict_dirs()

    def op(col: Collection) -> None:
        for dict_dir in legacy_dicts:
            WiktionaryFetcher.migrate_dict_to_sqlite(dict_dir, consts.dicts_dir)

    def success(_: None) -> None:
        tooltip("Migrated Wiktionary dictionaries successfully")

    if legacy_dicts:
        query_op = QueryOp(parent=mw, op=op, success=success)
        if pointVersion() >= 50:
            query_op = query_op.with_progress(label="Migrating Wiktionary dictionaries")
        if pointVersion() >= 231000:
            query_op = query_op.without_collection()
        query_op.run_in_background()

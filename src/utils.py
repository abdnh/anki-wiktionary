from __future__ import annotations

from pathlib import Path

from .consts import consts


def get_legacy_dict_dirs() -> list[Path]:
    return [
        p
        for p in consts.userfiles_dir.iterdir()
        if p.is_dir() and p.name not in ("logs", consts.dicts_dir.name)
    ]


def get_dicts() -> list[Path]:
    return [p for p in (consts.dicts_dir).iterdir() if p.is_file()]


def get_dict_names() -> list[str]:
    return [p.stem for p in get_dicts()]

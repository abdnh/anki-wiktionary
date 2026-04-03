from __future__ import annotations

from collections.abc import Generator, Iterable
from pathlib import Path
from typing import TypeVar

from .consts import consts


def get_legacy_dict_dirs() -> list[Path]:
    return [p for p in consts.userfiles_dir.iterdir() if p.is_dir() and p.name not in ("logs", consts.dicts_dir.name)]


def get_dicts() -> list[Path]:
    return [p for p in (consts.dicts_dir).iterdir() if p.is_file()]


def get_dict_names() -> list[str]:
    return [p.stem for p in get_dicts()]


T = TypeVar("T")


def batched(iterable: Iterable[T], n: int) -> Generator[list[T], None, None]:
    batch: list[T] = []
    for item in iterable:
        if len(batch) < n:
            batch.append(item)
        else:
            yield batch
            batch.clear()
    if batch:
        yield batch

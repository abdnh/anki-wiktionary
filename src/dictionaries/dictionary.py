from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Type

if TYPE_CHECKING:
    from .parser import Parser


class DictException(Exception):
    pass


@dataclass
class DictEntry:
    word: str
    definitions: list[str]
    examples: list[str]
    gender: str
    pos: str
    inflections: str
    translations: str


class Dictionary(ABC):
    name: str
    ext: str
    desc: str
    parsers: list[Type[Parser]] = []

    def __init__(self, path: Path):
        self.dict_dir = path

    @classmethod
    @abstractmethod
    def build_dict(
        cls,
        filename: str | Path,
        output_folder: Path,
        on_progress: Callable[[int], bool],
        on_error: Callable[[str, Exception], None],
    ) -> int | None:
        raise NotImplementedError()

    def lookup(self, query: str, parser: Parser) -> DictEntry | None:
        assert parser.__class__ in self.parsers
        return None

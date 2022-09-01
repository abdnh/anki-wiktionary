from pathlib import Path
from typing import List, Tuple, Type

from ..consts import USER_FILES
from .dictionary import DictEntry, DictException, Dictionary
from .kaikki import KaikkiDict
from .parser import Parser
from .zim import ZIMDict

dictionary_classes: List[Type[Dictionary]] = [KaikkiDict, ZIMDict]


def get_dictionaries() -> List[Tuple[Type[Dictionary], List[Path]]]:
    dict_tuples: List[Tuple[Type[Dictionary], List[Path]]] = []
    for dict_class in dictionary_classes:
        provider_path = USER_FILES / dict_class.name
        provider_path.mkdir(exist_ok=True)
        dictionary_paths = [path for path in provider_path.iterdir() if path.is_dir()]
        dict_tuples.append((dict_class, dictionary_paths))
    return dict_tuples

from typing import List, Type

from .dictionary import DictEntry, DictException, Dictionary
from .kaikki import KaikkiDict
from .parser import Parser
from .zim import ZIMDict

dictionary_classes: List[Type[Dictionary]] = [KaikkiDict, ZIMDict]

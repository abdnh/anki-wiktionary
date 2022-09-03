from __future__ import annotations

import functools
import shutil
from pathlib import Path
from typing import Callable, Type

import spacy
from bs4 import BeautifulSoup
from bs4.element import NavigableString, PageElement, Tag
from zimply_core.zim_core import ZIMClient

from .dictionary import DictEntry, DictException, Dictionary
from .parser import Parser
from .utils import strip_punct


def get_next_sibling_element(element: Tag) -> PageElement | None:
    sibling = element.next_sibling
    while isinstance(sibling, NavigableString):
        sibling = sibling.next_sibling
    return sibling


def get_prev_sibling_element(element: Tag) -> PageElement | None:
    sibling = element.previous_sibling
    while isinstance(sibling, NavigableString):
        sibling = sibling.previous_sibling
    return sibling


def strip_images(element: Tag) -> None:
    for img in element.find_all("img"):
        img.decompose()


class GreekParser(Parser):
    """
    ZIM Parser for Greek Wiktionary.
    Only tested with wiktionary_el_all_maxi_2022-07.zim and has many issues.
    """

    name = "Greek"

    def __init__(self) -> None:
        self.nlp = spacy.load("el_core_news_sm")
        super().__init__()

    def _stem(self, word: str) -> str:
        doc = self.nlp(word)
        lemmas = []
        for token in doc:
            lemmas.append(token.lemma_)
        return " ".join(lemmas)

    # HTML IDs one of which is assumed to exist in the queried page
    LANG_IDS = [
        r"#Ελληνικά_\(el\)",
        r"#Αρχαία_ελληνικά_\(grc\)",
        r"#Μεσαιωνικά_ελληνικά_\(gkm\)",
    ]

    # Greek parts of speech used to detect parts of speech and definitions
    POS_LABELS = [
        "άρθρο",
        "ουσιαστικό",
        "επίθετο",
        "αντωνυμία",
        "ρήμα",
        "κλιτή μετοχή",
        "άκλιτη μετοχή",
        "επίρρημα",
        "σύνδεσμος",
        "πρόθεση",
        "επιφώνημα",
        "ρηματικός τύπος",
        "επιθέτου",
        "ουσιαστικού",
        "αριθμητικό",
        "συντομομορφή",
        "αριθμητικού",
        "όνομα",
        "μετοχή",
        "μόριο",
        "αντωνυμία",
        "μετοχής",
        "προστακτική",
        "εκφράσεις",
        "αντωνυμίας",
    ]

    def lookup(self, query: str, dictionary: Dictionary) -> DictEntry | None:
        assert isinstance(dictionary, ZIMDict)
        forms = [query, query.lower(), query.title(), query.upper(), self._stem(query)]
        soup = None
        for form in forms:
            try:
                soup = dictionary.get_soup(dictionary.zim_client, form)
                break
            except KeyError:
                pass
        if not soup:
            return None
        pos: list[str] = []
        gender: list[str] = []
        definitions: list[str] = []
        inflections = ""
        translations = ""
        greek_el = None
        for lang_id in self.LANG_IDS:
            greek_el = soup.select_one(lang_id)
            if greek_el:
                break
        if greek_el:
            parent_details = greek_el.find_parents("details")[0]
            inflection_table_el = parent_details.select_one("table")
            if inflection_table_el:
                inflections = inflection_table_el.decode()
            for entry in parent_details.select("details"):
                strip_images(entry)
                summary_el = entry.find("summary")
                translation_h = entry.select_one("#Μεταφράσεις")
                if summary_el:
                    possible_pos = summary_el.get_text()
                    summary_el_title = summary_el.get("title", "")
                    if any(
                        l.lower() in possible_pos.lower() for l in self.POS_LABELS
                    ) or any(
                        l.lower() in summary_el_title.lower() for l in self.POS_LABELS
                    ):
                        pos.append(possible_pos)
                    elif translation_h:
                        translations = entry.decode_contents()
                        continue
                    else:
                        continue
                    summary_el.decompose()
                # We're dumping all the entry contents here, which include parts of speech, example sentences, etc.
                # FIXME: find a consistent structure to parse this mess
                definitions.append(entry.decode_contents())

        return DictEntry(
            query,
            definitions,
            [],
            "<br>".join(gender),
            "<br>".join(pos),
            inflections,
            translations,
        )


class SpanishParser(Parser):
    """
    ZIM Parser for Spanish Wiktionary.
    Only tested with wiktionary_es_all_maxi_2022-07.
    Definition importing could use a lot of improvement.
    """

    name = "Spanish"

    # Spanish parts of speech used to detect parts of speech and definitions
    POS_LABELS = [
        "sustantivo",
        "nombre",
        "preposición",
        "pronombre",
        "verbo",
        "interjección",
        "conjunción",
        "adjetivo",
        "adverbio",
        "forma verbal",
        "forma sustantiva",
        "forma adjetiva",
        "participio",
        "artículo determinado",
        "expresión",
    ]

    def lookup(self, query: str, dictionary: Dictionary) -> DictEntry | None:
        assert isinstance(dictionary, ZIMDict)
        try:
            soup = dictionary.get_soup(dictionary.zim_client, query)
        except KeyError:
            return None
        pos: list[str] = []
        gender: list[str] = []
        definitions: list[str] = []
        inflections = ""
        translations = ""
        spanish_el = soup.select_one("#Español")
        if spanish_el:
            parent_details = spanish_el.find_parents("details")[0]
            inflection_table_el = parent_details.select_one(".inflection-table")
            if inflection_table_el:
                inflections = inflection_table_el.decode()
            for entry in parent_details.select("details"):
                strip_images(entry)
                summary_el = entry.find("summary")
                translation_h = entry.select_one("#Traducciones")
                possible_pos = ""
                if summary_el:
                    spans = summary_el.find_all("span")
                    if spans:
                        possible_pos = spans[0].get_text()
                        if len(spans) >= 3:
                            gender.append(spans[2].get_text())
                    else:
                        possible_pos = summary_el.get_text()
                    summary_el.decompose()
                if any(l in possible_pos.lower() for l in self.POS_LABELS):
                    pos.append(possible_pos)
                elif translation_h:
                    translations = entry.decode_contents()
                    continue
                else:
                    continue
                # We're dumping all the entry contents here, which include parts of speech, example sentences, etc.
                # FIXME: find a consistent structure to parse this mess
                definitions.append(entry.decode_contents())

        return DictEntry(
            query,
            definitions,
            [],
            "<br>".join(gender),
            "<br>".join(pos),
            inflections,
            translations,
        )


class ZIMDict(Dictionary):
    name = "ZIM"
    ext = "zim"
    desc = """Only a limited number of <a href="https://en.wikipedia.org/wiki/ZIM_(file_format)">ZIM</a> files listed at <a href="https://wiki.kiwix.org/wiki/Content_in_all_languages">this page</a> are supported currently."""
    parsers: list[Type[Parser]] = [GreekParser, SpanishParser]

    def __init__(self, path: Path):
        super().__init__(path)
        zim_path = next(path.glob("*.zim"), None)
        if not zim_path:
            raise DictException(f"No zim file was found in {str(path)}")
        self.zim_client = ZIMClient(
            zim_path, encoding="utf-8", auto_delete=True, enable_search=False
        )

    @classmethod
    def build_dict(
        cls,
        filename: str | Path,
        output_folder: Path,
        on_progress: Callable[[int], bool],
        on_error: Callable[[str, Exception], None],
    ) -> int | None:
        # just copy input zim file to the output folder
        output_folder.mkdir(exist_ok=True)
        shutil.copy(filename, output_folder)
        return None

    @staticmethod
    @functools.lru_cache
    def get_soup(zim_client: ZIMClient, query: str) -> BeautifulSoup:
        article = zim_client.get_article(query)
        soup = BeautifulSoup(article.data.decode(), "html.parser")
        return soup

    def lookup(self, query: str, parser: Parser) -> DictEntry | None:
        query = strip_punct(query)
        super().lookup(query, parser)
        return parser.lookup(query, self)

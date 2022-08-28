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


class GreekParser(Parser):
    """
    ZIM Parser for Greek Wiktionary.
    Only tested with wiktionary_el_all_maxi_2022-07.zim and has some issues.
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
        definitions: list[str] = []
        examples: list[str] = []
        gender = ""
        pos = ""
        pos_el = soup.select_one(".partofspeech")
        if not pos_el:
            definitions_el = soup.select_one("pre")
            examples_el = soup.select_one("ol")
            if definitions_el:
                pos = get_prev_sibling_element(definitions_el).contents[-1].get_text()
                definitions = [definitions_el.get_text()]
            if examples_el:
                examples = [el.get_text() for el in examples_el.select("li")]
        else:
            pos = pos_el.get_text()
            nearest_parent = pos_el.parent.parent
            sibling = get_next_sibling_element(nearest_parent)
            if sibling.name in ("ol", "ul"):
                definitions_el = sibling
                definitions = [el.get_text() for el in definitions_el.select("li")]
            elif sibling.name == "p":
                definitions = [sibling.get_text()]
            else:
                gender_el = sibling
                gender = gender_el.decode()
                definitions_el = get_next_sibling_element(sibling)
                if not definitions_el:
                    redirect_str = soup.find(string="Δείτε επίσης")
                    if redirect_str:
                        el = get_next_sibling_element(redirect_str)
                        synonym = el.get_text()
                        return self.lookup(synonym, dictionary)
                else:
                    definitions = [el.get_text() for el in definitions_el.select("li")]

        return DictEntry(query, definitions, examples, gender, pos)


class SpanishParser(Parser):
    """
    ZIM Parser for Spanish Wiktionary.
    Only tested with wiktionary_es_all_maxi_2022-07.
    Definition importing could use a lot of improvement.
    """

    name = "Spanish"

    def lookup(self, query: str, dictionary: Dictionary) -> DictEntry | None:
        assert isinstance(dictionary, ZIMDict)
        try:
            soup = dictionary.get_soup(dictionary.zim_client, query)
        except KeyError:
            return None
        pos_labels = [
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
        pos: list[str] = []
        gender: list[str] = []
        definitions: list[str] = []
        spanish_el = soup.select_one("#Español")
        if spanish_el:
            parent_details = spanish_el.find_parents("details")[0]
            for entry in parent_details.select("details"):
                pos_gen_el = entry.find("summary")
                possible_pos = ""
                if pos_gen_el:
                    spans = pos_gen_el.find_all("span")
                    if spans:
                        print(spans, len(spans))
                        possible_pos = spans[0].get_text()
                        if len(spans) >= 3:
                            gender.append(spans[2].get_text())
                    else:
                        possible_pos = pos_gen_el.get_text()
                if any(l in possible_pos.lower() for l in pos_labels):
                    pos.append(possible_pos)
                else:
                    continue
                definitions.append(entry.decode_contents())

        return DictEntry(query, definitions, [], "<br>".join(gender), "<br>".join(pos))


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
        super().lookup(query, parser)
        return parser.lookup(query, self)

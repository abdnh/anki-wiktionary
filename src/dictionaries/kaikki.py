from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Callable, Type

from .dictionary import DictEntry, Dictionary
from .parser import Parser
from .utils import strip_punct


class GeneralParser(Parser):
    name = "General"

    def lookup(self, query: str, dictionary: Dictionary) -> DictEntry | None:
        assert isinstance(dictionary, KaikkiDict)
        try:
            data = dictionary.get_json(dictionary.dict_dir, query)
        except FileNotFoundError:
            return None
        definitions = [
            "\n".join(d.get("raw_glosses", [])) for d in data.get("senses", [])
        ]
        examples = []
        for sense in data.get("senses", []):
            for example in sense.get("examples", []):
                sent = example["text"]
                if example.get("english"):
                    sent += f" / {example['english']}"
                examples.append(sent)
        genders = {"feminine", "masculine", "neuter"}
        forms = data.get("forms", [])
        gender = ""
        # FIXME: do we need to return the form too along with the gender? and can different forms have different genders?
        for form in forms:
            for g in genders:
                if g in form.get("tags", []):
                    gender = g
        pos = data.get("pos", "")
        return DictEntry(query, definitions, examples, gender, pos, "", "")


class KaikkiDict(Dictionary):
    name = "Kaikki"
    ext = "json"
    desc = """To import from <a href="https://kaikki.org/">Kaikki</a>, find your target dictionary in their <a href="https://kaikki.org/dictionary/">dictionary list</a> and enter its page.<br>
    You should find there at the bottom of the page a link to download a JSON file (which has a name like "kaikki.org-dictionary-Russian.json")<br>containing all word senses that you can import to Anki here.
    """
    parsers: list[Type[Parser]] = [GeneralParser]

    @classmethod
    def build_dict(
        cls,
        filename: str | Path,
        output_folder: Path,
        on_progress: Callable[[int], bool],
        on_error: Callable[[str, Exception], None],
    ) -> int | None:
        """Dumps a JSON file downloaded from https://kaikki.org/dictionary/{lang}/
        to separate files for each entry in 'dictionary'"""
        output_folder.mkdir(exist_ok=True)
        count = 0
        with open(filename, encoding="utf-8") as file:
            for i, line in enumerate(file):
                entry = json.loads(line)
                word = entry["word"]
                try:
                    with open(
                        output_folder / f"{word}.json",
                        mode="w",
                        encoding="utf-8",
                    ) as outfile:
                        outfile.write(line)
                        count += 1
                except Exception as exc:
                    on_error(word, exc)
                if i % 50 == 0:
                    if not on_progress(i + 1):
                        break
        return count

    @staticmethod
    @functools.lru_cache
    def get_json(dict_dir: Path, word: str) -> dict:
        with open(dict_dir / f"{word}.json", encoding="utf-8") as file:
            return json.load(file)

    def lookup(self, query: str, parser: Parser) -> DictEntry | None:
        query = strip_punct(query)
        super().lookup(query, parser)
        return parser.lookup(query, self)

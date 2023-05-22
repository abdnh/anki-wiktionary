from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Callable

from . import consts


class WiktionaryError(Exception):
    pass


class WordNotFoundError(WiktionaryError):
    pass


class WiktionaryFetcher:
    def __init__(self, dictionary: str, base_dir: Path = consts.USER_FILES):
        self.dict_dir = base_dir / dictionary

    @classmethod
    def dump_kaikki_dict(
        cls,
        filename: str | Path,
        dictionary: str,
        on_progress: Callable[[int], bool],
        on_error: Callable[[str, Exception], None],
        base_dir: Path = consts.USER_FILES,
    ) -> int:
        """Dumps a JSON file downloaded from https://kaikki.org/dictionary/{lang}/
        to separate files for each entry in 'dictionary'"""
        outdir = base_dir / dictionary
        outdir.mkdir(exist_ok=True)
        count = 0
        with open(filename, encoding="utf-8") as file:
            for i, line in enumerate(file):
                entry = json.loads(line)
                word = entry["word"]
                try:
                    with open(
                        outdir / f"{word}.json",
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
    def _get_word_json(dict_dir: Path, word: str) -> dict:
        # TODO: handle words with multiple word senses

        try:
            with open(dict_dir / f"{word}.json", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError as exc:
            raise WordNotFoundError(
                f'"{word}" was not found in the dictionary.'
            ) from exc

    def get_word_json(self, word: str) -> dict:
        return self._get_word_json(self.dict_dir, word)

    def get_senses(self, word: str) -> list[str]:
        data = self.get_word_json(word)
        return [
            "\n".join(d.get("raw_glosses", d.get("glosses", [])))
            for d in data.get("senses", [])
        ]

    def get_examples(self, word: str) -> list[str]:
        data = self.get_word_json(word)
        examples = []
        for sense in data.get("senses", []):
            for example in sense.get("examples", []):
                sent = example["text"]
                if example.get("english"):
                    sent += f" / {example['english']}"
                examples.append(sent)
        return examples

    def get_gender(self, word: str) -> str:
        genders = {"feminine", "masculine", "neuter", "common-gender"}
        data = self.get_word_json(word)
        # forms = data.get("senses", []) + data.get("forms", [])
        senses = data.get("senses", [])
        # FIXME: do we need to return the form too along with the gender? and can different forms have different genders?
        for form in senses:
            for gender in genders:
                if gender in form.get("tags", []):
                    return gender

        # Latin words have their genders in "forms"
        forms = data.get("forms", [])
        for form in forms:
            for gender in genders:
                tags = form.get("tags", [])
                if gender in tags and "canonical" in tags:
                    return gender

        return ""

    def get_part_of_speech(self, word: str) -> str:
        data = self.get_word_json(word)
        return data.get("pos", "")

    def get_ipa(self, word: str) -> str:
        data = self.get_word_json(word)
        sounds = data.get("sounds", [])
        for sound in sounds:
            if sound.get("ipa"):
                return sound["ipa"]
        return ""

    def get_audio_url(self, word: str) -> str:
        data = self.get_word_json(word)
        sounds = data.get("sounds", [])
        for sound in sounds:
            if sound.get("ogg_url"):
                return sound["ogg_url"]
        return ""

    def get_etymology(self, word: str) -> str:
        data = self.get_word_json(word)
        return data.get("etymology_text", "")

    # "declension": forms in the declension table
    def get_declension(self, word: str) -> dict[str, list[str]]:
        declensions: dict[str, list[str]] = {}

        data = self.get_word_json(word)
        forms = data.get("forms", [])

        for form in forms:
            if (
                isinstance(form.get("source"), str)
                and form.get("source").lower() == "declension"
            ):
                # "table-tags" and "inflection-template" seems like useless stuffs
                useless_tags = ["table-tags", "inflection-template"]
                for useless_tag in useless_tags:
                    if useless_tag in form.get("tags"):
                        break

                else:
                    # append {"tags": "form"} to `declensions`
                    key = ", ".join(form.get("tags"))
                    value = form.get("form")
                    declensions.update({key: declensions.get(key, []) + [value]})

        return declensions


if __name__ == "__main__":
    dictionary = WiktionaryFetcher("Russian")
    words = ["кошка"]
    for word in words:
        print(dictionary.get_senses(word))
        print(dictionary.get_examples(word))
        print(dictionary.get_senses(word))

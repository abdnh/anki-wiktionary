from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Callable


class WiktionaryError(Exception):
    pass


class WordNotFoundError(WiktionaryError):
    def __init__(self, word: str):
        self.word = word

    def __str__(self) -> str:
        return f'"{self.word}" was not found in the dictionary.'


class WiktionaryFetcher:
    def __init__(self, dictionary: str, base_dir: Path):
        self.db_path = base_dir / f"{dictionary}.db"
        self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS words (
                word text,
                data text
            );
            CREATE INDEX IF NOT EXISTS index_word ON words(word);
        """
        )

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> WiktionaryFetcher:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_tb: Any) -> None:
        self.close()

    def _add_word(self, word: str, data: str) -> None:
        self._connection.execute("INSERT INTO words(word, data) values(?, ?)", (word, data))

    # pylint: disable=too-many-arguments
    @classmethod
    def import_kaikki_dict(
        cls,
        filename: str | Path,
        dictionary: str,
        on_progress: Callable[[int], bool],
        on_error: Callable[[str, Exception], None],
        base_dir: Path,
    ) -> int:
        """Dumps a JSON file downloaded from https://kaikki.org/dictionary/{lang}/
        to a SQLite database"""
        base_dir.mkdir(exist_ok=True)
        count = 0
        with open(filename, encoding="utf-8") as file:
            with WiktionaryFetcher(dictionary, base_dir) as fetcher:
                for i, line in enumerate(file):
                    try:
                        entry = json.loads(line)
                        word = entry["word"]
                        fetcher._add_word(word, line)
                        count += 1
                    except Exception as exc:
                        print(f"{exc=}")
                        on_error(word, exc)
                    if i % 50 == 0:
                        if not on_progress(i + 1):
                            break
                fetcher._connection.commit()
        return count

    @classmethod
    def migrate_dict_to_sqlite(cls, dictionary_dir: Path, new_dir: Path) -> None:
        with WiktionaryFetcher(dictionary_dir.name, new_dir) as fetcher:
            for file in dictionary_dir.iterdir():
                fetcher._add_word(file.stem, file.read_text(encoding="utf-8"))
            fetcher._connection.commit()
        shutil.rmtree(dictionary_dir)

    def get_word_json(self, word: str) -> dict:
        # TODO: handle words with multiple word senses
        row = self._connection.execute("SELECT data FROM words WHERE word = ?", (word,)).fetchone()
        if not row:
            raise WordNotFoundError(word)
        return json.loads(row[0])

    def get_senses(self, word: str) -> list[str]:
        data = self.get_word_json(word)
        return ["\n".join(d.get("raw_glosses", d.get("glosses", []))) for d in data.get("senses", [])]

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
        # FIXME: do we need to return the form too along with the gender?
        # and can different forms have different genders?
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
            if isinstance(form.get("source"), str) and form.get("source").lower() == "declension":
                tags = form.get("tags", [])
                # "table-tags" and "inflection-template" seems like useless stuffs
                useless_tags = ["table-tags", "inflection-template"]
                for useless_tag in useless_tags:
                    if useless_tag in tags:
                        break

                else:
                    # append {"tags": "form"} to `declensions`
                    key = ", ".join(tags)
                    value = form.get("form")
                    declensions.update({key: declensions.get(key, []) + [value]})

        return declensions


if __name__ == "__main__":
    dictionary = WiktionaryFetcher("Russian", Path("dictionaries"))
    words = ["кошка"]
    for word in words:
        print(dictionary.get_senses(word))
        print(dictionary.get_examples(word))
        print(dictionary.get_senses(word))

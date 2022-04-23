import json
import functools
from typing import Callable, List, Dict

from . import consts


class WiktionaryError(Exception):
    pass


class WordNotFoundError(WiktionaryError):
    pass


class WiktionaryFetcher:
    def __init__(self, dictionary: str):
        self.dict_dir = consts.USER_FILES / dictionary

    @classmethod
    def dump_kaikki_dict(
        cls,
        filename: str,
        dictionary: str,
        on_progress: Callable[[int], None],
        on_error: Callable[[str, Exception], None],
    ) -> int:
        """Dumps a JSON file downloaded from https://kaikki.org/dictionary/{lang}/
        to separate files for each entry in 'dictionary'"""
        outdir = consts.USER_FILES / dictionary
        outdir.mkdir(exist_ok=True)
        count = 0
        with open(filename, encoding="utf-8") as f:
            for i, line in enumerate(f):
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
                    on_progress(i + 1)
        return count

    @functools.lru_cache
    def _get_word_json(self, word: str) -> Dict:
        try:
            with open(self.dict_dir / f"{word}.json", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as exc:
            raise WordNotFoundError(
                f'"{word}" was not found in the dictionary.'
            ) from exc

    def get_senses(self, word: str) -> List[str]:
        data = self._get_word_json(word)
        return ["\n".join(d.get("raw_glosses", [])) for d in data.get("senses", [])]

    def get_examples(self, word: str) -> List[str]:
        data = self._get_word_json(word)
        examples = []
        for sense in data.get("senses", []):
            for example in sense.get("examples", []):
                sent = example["text"]
                if example.get("english"):
                    sent += f" / {example['english']}"
                examples.append(sent)
        return examples

    def get_gender(self, word: str) -> str:
        genders = {"feminine", "masculine", "neuter"}
        data = self._get_word_json(word)
        forms = data.get("forms", [])
        # FIXME: do we need to return the form too along with the gender? and can different forms have different genders?
        for form in forms:
            for gender in genders:
                if gender in form.get("tags", []):
                    return gender
        return ""

    def get_part_of_speech(self, word: str) -> str:
        data = self._get_word_json(word)
        return data.get("pos", "")


if __name__ == "__main__":
    dictionary = WiktionaryFetcher("Russian")
    words = ["кошка"]
    for word in words:
        print(dictionary.get_senses(word))
        print(dictionary.get_examples(word))
        print(dictionary.get_senses(word))

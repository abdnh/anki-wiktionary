import builtins
import tempfile
import unittest
from pathlib import Path
from typing import Any, Union
from unittest.mock import patch

from src.dictionaries.kaikki import GeneralParser, KaikkiDict


def mock_open(file: Union[str, Path], *args: Any, **kwargs: Any) -> Any:
    # Make importing artifically fail for a certain file
    if file == "FAIL.json" or getattr(file, "name", "") == "FAIL.json":
        raise Exception("FAIL")
    return builtins.open(file, *args, **kwargs)  # pylint: disable=unspecified-encoding


class TestKaikkiDict(unittest.TestCase):
    DICT_NAME = "dict"

    def test_importing(self) -> None:
        patcher = patch("src.dictionaries.kaikki.open", side_effect=mock_open)
        patcher.start()
        failed_words = []

        def on_error(word: str, exc: Exception) -> None:
            assert str(exc) == "FAIL"
            failed_words.append(word)

        tests_dir = Path(__file__).parent
        with tempfile.TemporaryDirectory() as tmp_dir_s:
            tmp_dir = Path(tmp_dir_s)
            count = KaikkiDict.build_dict(
                tests_dir / "test_dict.json",
                tmp_dir / self.DICT_NAME,
                on_progress=lambda _: True,
                on_error=on_error,
            )
            assert count == 2
            assert len(failed_words) == 1
            assert failed_words[0] == "FAIL"
            patcher.stop()
            fetcher = KaikkiDict(tmp_dir / self.DICT_NAME)
            parser = GeneralParser()
            entry = fetcher.lookup("кошка", parser)
            assert entry.gender == "feminine"
            assert entry.definitions[0] == "cat"
            assert entry.pos == "noun"
            assert (
                entry.examples[0]
                == "жить как ко́шка с соба́кой / to lead a cat-and-dog life"
            )
            assert fetcher.lookup("FAIL", parser) is None

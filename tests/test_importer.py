from __future__ import annotations

import tempfile
from pathlib import Path

from src.fetcher import WiktionaryFetcher


def test_importing() -> None:
    tests_dir = Path(__file__).parent
    with tempfile.TemporaryDirectory() as tmp_dir_s:
        tmp_dir = Path(tmp_dir_s)
        count = WiktionaryFetcher.import_kaikki_dict(
            tests_dir / "test_dict.json",
            "dict",
            on_progress=lambda *args, **kwargs: True,
            on_error=lambda *args, **kwargs: None,
            base_dir=tmp_dir,
        )
        assert count == 2
        with WiktionaryFetcher("dict", base_dir=tmp_dir) as fetcher:
            assert fetcher.get_gender("кошка") == "feminine"
            assert fetcher.get_senses("кошка")[0] == "cat"
            assert fetcher.get_part_of_speech("кошка") == "noun"
            assert (
                fetcher.get_examples("кошка")[0]
                == "жить как ко́шка с соба́кой / to lead a cat-and-dog life"
            )

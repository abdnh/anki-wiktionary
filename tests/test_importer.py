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
            word = "кошка"
            assert fetcher.get_gender(word) == "feminine"
            assert fetcher.get_senses(word)[0] == "cat"
            assert fetcher.get_part_of_speech(word) == "noun"
            assert fetcher.get_examples(word)[0] == "жить как ко́шка с соба́кой / to lead a cat-and-dog life"
            assert fetcher.get_ipa(word) == "[ˈkoʂkə]"
            assert (
                fetcher.get_audio_url(word)
                == "https://upload.wikimedia.org/wikipedia/commons/f/f3/Ru-%D0%BA%D0%BE%D1%88%D0%BA%D0%B0.ogg"
            )
            assert (
                fetcher.get_etymology(word) == "From unattested Old East Slavic *ко́чька (*kóčĭka), "
                "from Proto-Slavic *kòťьka, from *kòťь, from *kòtъ. "
                "Cognate with Old Ruthenian ко́шка (kóška), Ukrainian кі́шка (kíška), Russian ко́шка (kóška)."
            )

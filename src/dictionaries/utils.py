import string

PUNCT_TRANS_TABLE = str.maketrans("", "", string.punctuation)


def strip_punct(text: str) -> str:
    return text.translate(PUNCT_TRANS_TABLE)

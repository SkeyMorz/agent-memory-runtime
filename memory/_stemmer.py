"""Lightweight English stemmer — no external dependencies."""

import re

STEP2_SUFFIXES = (
    "ational", "tional", "enci", "anci", "izer", "abli", "alli", "entli",
    "eli", "ousli", "ization", "ation", "ator", "alism", "iveness",
    "fulness", "ousness", "aliti", "iviti", "biliti",
)

STEP3_SUFFIXES = (
    "icate", "ative", "alize", "iciti", "ical", "ful", "ness",
)


def stem(word: str) -> str:
    w = word.lower()
    if len(w) <= 2:
        return w

    if w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("ies"):
        w = w[:-2]
    elif w.endswith("ss"):
        pass
    elif w.endswith("s"):
        w = w[:-1]

    if w.endswith("eed"):
        w = w[:-1]
    elif w.endswith("ed"):
        w = w[:-2]
        if w.endswith("at") or w.endswith("bl") or w.endswith("iz"):
            w += "e"
        elif len(w) >= 2 and w[-1] == w[-2] and w[-1] not in "lsz":
            w = w[:-1]
    elif w.endswith("ing"):
        w = w[:-3]
        if w.endswith("at") or w.endswith("bl") or w.endswith("iz"):
            w += "e"
        elif len(w) >= 2 and w[-1] == w[-2] and w[-1] not in "lsz":
            w = w[:-1]

    if w.endswith("y") and len(w) >= 2 and w[-2] not in "aeiou":
        w = w[:-1] + "i"

    for suffix in STEP2_SUFFIXES:
        if w.endswith(suffix) and len(w) > len(suffix) + 1:
            if suffix == "ational":
                w = w[:-7] + "ate"
            elif suffix == "tional":
                w = w[:-6] + "tion"
            elif suffix == "enci":
                w = w[:-4] + "ence"
            elif suffix == "anci":
                w = w[:-4] + "ance"
            elif suffix == "izer":
                w = w[:-4] + "ize"
            elif suffix == "abli":
                w = w[:-4] + "able"
            elif suffix == "alli":
                w = w[:-4] + "al"
            elif suffix in ("entli", "eli", "ousli"):
                w = w[:-2]
            elif suffix in ("ization", "ation"):
                w = w[:-5] + "e"
            elif suffix == "ator":
                w = w[:-4] + "ate"
            elif suffix == "alism":
                w = w[:-5] + "al"
            elif suffix in ("iveness", "fulness", "ousness"):
                w = w[:-4]
            elif suffix == "aliti":
                w = w[:-5] + "al"
            elif suffix == "iviti":
                w = w[:-5] + "ive"
            elif suffix == "biliti":
                w = w[:-6] + "ble"
            break

    for suffix in STEP3_SUFFIXES:
        if w.endswith(suffix) and len(w) > len(suffix) + 1:
            if suffix == "icate":
                w = w[:-5] + "ic"
            elif suffix == "ative":
                w = w[:-5]
            elif suffix == "alize":
                w = w[:-5] + "al"
            elif suffix == "iciti":
                w = w[:-5] + "ic"
            elif suffix in ("ical", "ful", "ness"):
                w = w[:-len(suffix)]
            break

    if len(w) >= 2 and w[-1] == "e":
        w = w[:-1]
    if len(w) >= 2 and w[-1] == w[-2] and w[-1] == "l":
        w = w[:-1]

    return w


def tokenize_and_stem(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    return [stem(t) for t in tokens if len(t) > 1]

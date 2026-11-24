"""Readable concept URIs: <ConceptScheme URI>/<LocalName>.

Column B of template v9 holds only the local name (e.g. "Rekkverk"); the full URI is
the ConceptScheme URI (cell B1) + "/" + the name, put together by the tools.

The local name is the main-language prefLabel in CamelCase, transliterated to
ASCII (ø -> o, æ -> ae, å -> always aa). Acronyms (words written fully in capitals) stay
in capitals. Examples: "brystningshøyde" -> "Brystningshoyde", "skråstagbru" -> "Skraastagbru",
"CE-merket produkt" -> "CEMerketProdukt", "single crochet" -> "SingleCrochet". Clashes between languages (US double crochet = UK treble crochet) are
documented in scope notes, not in the name.
"""
from __future__ import annotations

import re
import unicodedata

# CamelCase concept name: letters and digits only
LOCAL_NAME_RE = re.compile(r"^[A-Za-z0-9]+$")
_TRANSLIT = {"æ": "ae", "Æ": "Ae", "ø": "o", "Ø": "O", "å": "aa", "Å": "Aa",
             "ä": "ae", "Ä": "Ae", "ö": "oe", "Ö": "Oe", "ü": "ue", "Ü": "Ue", "ß": "ss"}


def ascii_fold(text: str) -> str:
    """Transliterate to ASCII: æ -> ae, ø -> o, å -> aa, ä -> ae, ö -> oe, ü -> ue, ß -> ss; other accents dropped."""
    text = "".join(_TRANSLIT.get(ch, ch) for ch in text)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def local_name(label: str) -> str:
    """CamelCase local name from a term: each word capitalised, the rest lowercased,
    except acronyms (all capitals, e.g. CE, IP, NIB), which are kept as written."""
    words = re.split(r"[^A-Za-z0-9]+", ascii_fold(label or ""))
    def word(w):
        """Capitalise one word; a word of two or more capital letters (an acronym) is kept."""
        letters = [ch for ch in w if ch.isalpha()]
        if len(letters) >= 2 and all(ch.isupper() for ch in letters):
            return w
        return w[:1].upper() + w[1:].lower()
    return "".join(word(w) for w in words if w)


def local_part(uri: str, scheme_uri: str | None) -> str | None:
    """'…/N101/Rekkverk' -> 'Rekkverk' if the URI is under the scheme URI, else None."""
    if not uri or not scheme_uri:
        return None
    prefix = scheme_uri.rstrip("/") + "/"
    return uri[len(prefix):] if uri.startswith(prefix) else None


def expected_name(c, label_field: str) -> str:
    """Name the generator would give: CamelCase of the main-language term."""
    return local_name(c.get(label_field) or "")


def concept_uri(scheme_uri: str, name: str) -> str:
    """<ConceptScheme URI>/<name>."""
    return scheme_uri.rstrip("/") + "/" + name


def assign_names(concepts, label_field: str, overwrite: bool = False, main_lang: str = "nb") -> dict:
    """Return {concept key: local name} for concepts without a name in column B (or all, with overwrite).

    Collisions get a numeric suffix (Name2, Name3 …) and are listed under "_collisions".
    """
    taken = {c.get("uri") for c in concepts if c.get("uri") and not overwrite}
    out, collisions = {}, []
    for c in concepts:
        if c.get("uri") and not overwrite:
            continue
        base = expected_name(c, label_field) or c.key.replace("-", "")
        name, n = base, 1
        while name in taken:
            n += 1
            name = f"{base}{n}"
        if n > 1:
            collisions.append((c.key, base, name))
        taken.add(name)
        out[c.key] = name
    out["_collisions"] = collisions
    return out


# ---------------------------------------------------------------- Excel formula for column B
# Column B (concept name) can be a formula over column C (main-language term). The formula follows local_name:
# transliteration, words split at spaces and punctuation, each word capitalised with the rest lower case, words written
# fully in capitals (acronyms) kept. Excel 365/2021 (LET). Up to NAME_WORDS words; a name typed into B replaces the formula.
NAME_WORDS = 20
_FORMULA_TRANSLIT = [("æ", "ae"), ("Æ", "Ae"), ("ø", "o"), ("Ø", "O"), ("å", "aa"), ("Å", "Aa"), ("ä", "ae"), ("Ä", "Ae"),
                     ("ö", "oe"), ("Ö", "Oe"), ("ü", "ue"), ("Ü", "Ue"), ("ß", "ss"), ("é", "e"), ("è", "e"), ("ê", "e"),
                     ("É", "E"), ("á", "a"), ("à", "a"), ("ó", "o"), ("ò", "o"), ("ô", "o"), ("í", "i"), ("ú", "u"),
                     ("ñ", "n"), ("ç", "c")]
_FORMULA_SEPARATORS = ["-", "–", "—", "/", "\\", ",", ".", ":", ";", "(", ")", "[", "]", "'", "’", '"', "«", "»", "&",
                       "+", "*", "%", "§", "?", "!", "=", "<", ">", "|", "_", " "]


def name_formula(label_cell: str) -> str:
    """Excel formula (file syntax) that makes the concept name from the term in label_cell, e.g. 'C25'."""
    x = label_cell
    for a, b in _FORMULA_TRANSLIT:
        x = f'SUBSTITUTE({x},"{a}","{b}")'
    for sep in _FORMULA_SEPARATORS:
        x = f'SUBSTITUTE({x},"{sep.replace(chr(34), chr(34) * 2)}"," ")'
    parts = [f"_xlpm.t,TRIM({x})", '_xlpm.s,SUBSTITUTE(_xlpm.t," ",REPT(" ",200))']
    words = []
    for k in range(1, NAME_WORDS + 1):
        w = f"_xlpm.w{k}"
        parts.append(f"{w},TRIM(MID(_xlpm.s,{(k - 1) * 200 + 1},200))")
        words.append(f'IF({w}="","",IF(AND(LEN({w})>=2,EXACT({w},UPPER({w})),NOT(EXACT({w},LOWER({w})))),'
                     f'{w},UPPER(LEFT({w}))&LOWER(MID({w},2,200))))')
    return f'=IF(TRIM({label_cell})="","",_xlfn.LET({",".join(parts)},_xlfn.CONCAT({",".join(words)})))'


def name_formula_python(label: str) -> str:
    """The formula's logic in Python, to compare with local_name."""
    x = label or ""
    if not x.strip():
        return ""
    for a, b in _FORMULA_TRANSLIT:
        x = x.replace(a, b)
    for sep in _FORMULA_SEPARATORS:
        x = x.replace(sep, " ")
    out = []
    for w in x.split()[:NAME_WORDS]:
        out.append(w if len(w) >= 2 and w == w.upper() and w != w.lower() else w[:1].upper() + w[1:].lower())
    return "".join(out)

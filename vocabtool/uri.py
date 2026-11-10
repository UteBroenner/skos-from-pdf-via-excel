"""Readable concept URIs: <ConceptScheme URI>/<LocalName>.

Column B of template v8 holds only the local name (e.g. "Rekkverk"); the full URI is
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
    text = "".join(_TRANSLIT.get(ch, ch) for ch in text)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def local_name(label: str) -> str:
    """CamelCase local name from a term: each word capitalised, the rest lowercased,
    except acronyms (all capitals, e.g. CE, IP, NIB), which are kept as written."""
    words = re.split(r"[^A-Za-z0-9]+", ascii_fold(label or ""))
    def word(w):
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

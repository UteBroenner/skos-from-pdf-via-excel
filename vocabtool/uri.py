"""Readable concept URIs: <ConceptScheme URI>/<LocalName>.

Column B of template v8 holds only the local name (e.g. "Rekkverk"); the full URI is
the ConceptScheme URI (cell B1) + "/" + the name, put together by the tools.

The local name is the main-language prefLabel in CamelCase, transliterated to
ASCII the way the v7 vocabularies did it (ø -> o, æ -> ae, å -> aa), e.g.
"brystningshøyde" -> "Brystningshoyde", "CE-merket produkt" -> "CeMerketProdukt",
"single crochet" -> "SingleCrochet".
"""
from __future__ import annotations

import re
import unicodedata

# CamelCase name, optionally with a language suffix for names that mean another concept in
# another language, e.g. DoubleCrochet-ENUS (US double crochet = UK treble crochet)
LOCAL_NAME_RE = re.compile(r"^[A-Za-z0-9]+(-[A-Z0-9]+)?$")
_TRANSLIT = {"æ": "ae", "Æ": "Ae", "ø": "o", "Ø": "O", "å": "aa", "Å": "Aa",
             "ä": "ae", "Ä": "Ae", "ö": "oe", "Ö": "Oe", "ü": "ue", "Ü": "Ue", "ß": "ss"}


def ascii_fold(text: str) -> str:
    text = "".join(_TRANSLIT.get(ch, ch) for ch in text)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def local_name(label: str) -> str:
    """CamelCase local name from a term: each word capitalised, the rest lowercased."""
    words = re.split(r"[^A-Za-z0-9]+", ascii_fold(label or ""))
    return "".join(w[:1].upper() + w[1:].lower() for w in words if w)


def local_part(uri: str, scheme_uri: str | None) -> str | None:
    """'…/N101/Rekkverk' -> 'Rekkverk' if the URI is under the scheme URI, else None."""
    if not uri or not scheme_uri:
        return None
    prefix = scheme_uri.rstrip("/") + "/"
    return uri[len(prefix):] if uri.startswith(prefix) else None


def lang_suffix(lang: str) -> str:
    """'en-US' -> 'ENUS', 'nb' -> 'NB'."""
    return re.sub(r"[^A-Za-z0-9]", "", lang).upper()


def cross_language_homonyms(concepts, label_field: str) -> set:
    """Keys of concepts whose main-language term is a label (any language, pref or alt)
    of a different concept under another language tag."""
    from .reader import label_fields, split_multi
    owners = {}
    for c in concepts:
        for fld, tag in label_fields(c.fields).items():
            if fld == label_field:
                continue
            vals = split_multi(c.get(fld)) if fld.startswith("alt_") else [c.get(fld)] if c.get(fld) else []
            for v in vals:
                owners.setdefault(v.strip().lower(), set()).add(c.key)
    return {c.key for c in concepts
            if c.get(label_field) and owners.get(c.get(label_field).strip().lower(), set()) - {c.key}}


def expected_name(c, label_field: str, main_lang: str, homonyms: set) -> str:
    base = local_name(c.get(label_field) or "")
    return f"{base}-{lang_suffix(main_lang)}" if base and c.key in homonyms else base


def concept_uri(scheme_uri: str, name: str) -> str:
    return scheme_uri.rstrip("/") + "/" + name


def assign_names(concepts, label_field: str, overwrite: bool = False, main_lang: str = "nb") -> dict:
    """Return {concept key: local name} for concepts without a name in column B (or all, with overwrite).

    Collisions get a numeric suffix (Name2, Name3 …) and are listed under "_collisions".
    """
    taken = {c.get("uri") for c in concepts if c.get("uri") and not overwrite}
    homonyms = cross_language_homonyms(concepts, label_field)
    out, collisions = {}, []
    for c in concepts:
        if c.get("uri") and not overwrite:
            continue
        base = expected_name(c, label_field, main_lang, homonyms) or c.key.replace("-", "")
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

"""Collections (skos:Collection) recorded in the main-language scope note.

Editors add a fixed sentence to the scope note of each member concept:

    Inngår i samlingen Hoveddata.
    Inngår i samlingene Skader, Inspeksjon.

Collection names are written as one would say them and separated by commas
(not "og", which may be part of a name). The scope note is the only place collections
are recorded; the tools build skos:Collection and skos:member from it.

- Collection URI: <ConceptScheme URI>/samling/<CamelCase of the name>
- skos:prefLabel of the collection: the name as written (main language)
- Only the main-language scope note is read. Collections are unordered and not nested.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .reader import Vocabulary, field_for
from .uri import local_name

SENTENCE_RE = re.compile(r"Inngår i samling(?P<form>en|ene)\s+(?P<names>[^.\n]+?)\s*\.(?=\s|$)")
MENTION_RE = re.compile(r"\bsamling", re.IGNORECASE)          # main language: looks like an attempt
OTHER_LANG_RE = re.compile(r"inng[åa]r i samling|part of the collection|teil der sammlung|parte de la colecci", re.IGNORECASE)


@dataclass
class Collection:
    name: str                       # CamelCase local name (URI part)
    label: str                      # name as first written
    members: list[str] = field(default_factory=list)   # concept keys, in workbook order
    spellings: set[str] = field(default_factory=set)


def scope_note_field(v: Vocabulary) -> str:
    return "scope_note" if v.main_lang == "nb" else field_for("scope_note", v.main_lang)


def parse_sentence(text: str | None) -> list[tuple[str, str]]:
    """[(form, name), ...] for every collection sentence in the text."""
    out = []
    for m in SENTENCE_RE.finditer(text or ""):
        out += [(m.group("form"), n.strip()) for n in m.group("names").split(",") if n.strip()]
    return out


def collection_uri(scheme_uri: str, name: str) -> str:
    return scheme_uri.rstrip("/") + "/samling/" + name


def collections(v: Vocabulary) -> dict[str, Collection]:
    """{CamelCase name: Collection} from the main-language scope notes."""
    fld = scope_note_field(v)
    out: dict[str, Collection] = {}
    for c in v.concepts:
        for _, label in parse_sentence(c.get(fld)):
            name = local_name(label)
            if not name:
                continue
            col = out.setdefault(name, Collection(name=name, label=label))
            col.spellings.add(label)
            if c.key not in col.members:
                col.members.append(c.key)
    return out


def sentence_problems(v: Vocabulary):
    """Yield (concept, rule, detail) for sentences the tools cannot use as written."""
    fld = scope_note_field(v)
    for c in v.concepts:
        main = c.get(fld) or ""
        parsed = parse_sentence(main)
        if MENTION_RE.search(main) and not parsed:
            yield c, "VT-COLL-SYNTAX", main[:120]
        for m in SENTENCE_RE.finditer(main):
            n = len([x for x in m.group("names").split(",") if x.strip()])
            if (m.group("form") == "en") != (n == 1):
                yield c, "VT-COLL-FORM", m.group(0)
        for f, val in c.fields.items():
            if f.startswith("scope_note") and f != fld and isinstance(val, str) and OTHER_LANG_RE.search(val):
                yield c, "VT-COLL-OTHER-LANG", f"{f}: {val[:100]}"


def rename_in_text(text: str, old: str, new: str) -> str:
    """Rename collection `old` (as written, or its CamelCase name) to `new` inside the sentences only."""
    def fix(m):
        names = [n.strip() for n in m.group("names").split(",")]
        names = [new if (n == old or local_name(n) == local_name(old)) else n for n in names]
        return f"Inngår i samling{m.group('form')} {', '.join(names)}."
    return SENTENCE_RE.sub(fix, text)


def outside_sentences(text: str, fn) -> str:
    """Apply fn to the parts of the text that are not collection sentences."""
    out, pos = [], 0
    for m in SENTENCE_RE.finditer(text):
        out += [fn(text[pos:m.start()]), m.group(0)]
        pos = m.end()
    return "".join(out + [fn(text[pos:])])

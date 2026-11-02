"""Draft scope notes that warn about label clashes, naming the other concept by ID.

Example: "Caution: 'treble crochet' is the UK name of this concept and the US name of
HEKL-0010 (treble crochet)." The notes are drafts for expert review.
"""
from __future__ import annotations

from collections import defaultdict

from .reader import Vocabulary, label_fields, split_multi

TAG_NAMES = {"en-US": "US", "en-GB": "UK", "en": "English", "nb": "Norwegian", "nn": "Nynorsk",
             "de": "German", "es": "Spanish", "sv": "Swedish", "da": "Danish", "fr": "French"}


def _kind(field: str, term: str) -> str:
    if field.startswith("label_"):
        return "name"
    letters = [ch for ch in term.lower() if ch.isalpha()]
    vowel_share = sum(ch in "aeiouyæøåäöü" for ch in letters) / max(1, len(letters))
    # abbreviations: short, contain digits, or are mostly consonants (sc2tog, FPdtr, sl st, invdec)
    is_abbr = len(term) <= 3 or any(ch.isdigit() for ch in term) or vowel_share < 0.35
    return "abbreviation" if is_abbr else "alternative name"


def _who(tags_kinds: set) -> str:
    """{('en-US','name'), ('en-GB','name')} -> 'US and UK name'."""
    by_kind = defaultdict(list)
    for tag, kind in sorted(tags_kinds):
        by_kind[kind].append(TAG_NAMES.get(tag, tag))
    return " and ".join(f"{' and '.join(t)} {k}" for k, t in by_kind.items())


def clash_notes(v: Vocabulary) -> dict[str, str]:
    by_key = v.by_key()
    uses = defaultdict(lambda: defaultdict(set))   # term -> key -> {(tag, kind)}
    shown = {}                                      # lowercase term -> spelling as first written
    for c in v.concepts:
        for fld, tag in label_fields(c.fields).items():
            vals = split_multi(c.get(fld)) if fld.startswith("alt_") else [c.get(fld)] if c.get(fld) else []
            for val in vals:
                uses[val.strip().lower()][c.key].add((tag, _kind(fld, val.strip())))
                shown.setdefault(val.strip().lower(), val.strip())
    notes = defaultdict(list)
    for term, per_key in sorted(uses.items()):
        if len(per_key) < 2:
            continue
        for key, mine in per_key.items():
            parts = []
            for other, theirs in sorted(per_key.items()):
                if other == key:
                    continue
                label = by_key[other].get(v.label_field) or ""
                ref = other if label.strip().lower() == term else f"{other} ({label})"
                parts.append(f"the {_who(theirs)} of {ref}")
            notes[key].append(f"'{shown[term]}' is the {_who(mine)} of this concept and {' and '.join(parts)}.")
    return {k: "Caution: " + " ".join(s) for k, s in notes.items()}

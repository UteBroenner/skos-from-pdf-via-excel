"""Rename a concept: change its name in column B and every reference to it.

References are updated in the relation columns (broader, isPartOf, related) and in notes
(scopeNote, editorialNote, any language). Column A and endringshash are formulas and follow by themselves.
"""
from __future__ import annotations

import re

import openpyxl

from .reader import read_workbook, RELATION_FIELDS, split_multi
from .uri import LOCAL_NAME_RE

NOTE_PREFIXES = ("scope_note", "editorial_note")


def rename(path: str, renames: dict[str, str]) -> dict:
    v = read_workbook(path)
    names = {c.get("uri") for c in v.concepts if c.get("uri")}
    for old, new in renames.items():
        if old not in names:
            raise ValueError(f"no concept named {old!r}")
        if not LOCAL_NAME_RE.match(new):
            raise ValueError(f"{new!r} is not a CamelCase name (letters and digits)")
        if new in names and new not in renames:
            raise ValueError(f"{new!r} is already used by another concept")
    wb = openpyxl.load_workbook(path)
    ws = wb["vokabular"]
    cols = {f: openpyxl.utils.column_index_from_string(L) for f, L in v.columns["vokabular"].items()}
    word = re.compile(r"(?<![A-Za-z0-9-])(" + "|".join(map(re.escape, sorted(renames, key=len, reverse=True))) + r")(?![A-Za-z0-9-])")
    counts = {"names": 0, "relations": 0, "notes": 0}
    for c in v.concepts:
        if c.get("uri") in renames:
            ws.cell(c.row, cols["uri"]).value = renames[c.get("uri")]
            counts["names"] += 1
        for fld in RELATION_FIELDS:
            vals = split_multi(c.get(fld))
            if any(t in renames for t in vals):
                ws.cell(c.row, cols[fld]).value = ", ".join(renames.get(t, t) for t in vals)
                counts["relations"] += sum(t in renames for t in vals)
        for fld, col in cols.items():
            if fld.startswith(NOTE_PREFIXES) and isinstance(c.get(fld), str) and word.search(c.get(fld)):
                ws.cell(c.row, col).value = word.sub(lambda m: renames[m.group(1)], c.get(fld))
                counts["notes"] += 1
    wb.save(path)
    return counts

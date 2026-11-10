"""Write reviewed values into concepts of a v8 workbook, by concept name (column B).

Input JSON: {"<concept name>": {"<field>": "<value>", ...}, ...}
Fields are the reader's field names (def_nb, source, relationship_with_source, editorial_note, scope_note, ...).
A field name ending in "+" appends to the current value, separated by a space (e.g. "editorial_note+").
Unknown concept names or fields are refused before anything is written. Formula columns are never written.
"""
from __future__ import annotations

import json
from pathlib import Path

import openpyxl

from .reader import read_workbook
from .template_ext import fit_table, apply_formulas

PROTECTED = {"identifier", "change_hash", "created_by", "uri"}


def set_fields(workbook, values: dict | str | Path, out=None) -> dict:
    if not isinstance(values, dict):
        values = json.loads(Path(values).read_text(encoding="utf-8"))
    v = read_workbook(workbook)
    by = v.by_key()
    col = {f: openpyxl.utils.column_index_from_string(L) for f, L in v.columns["vokabular"].items()}
    problems = [f"no concept named {k!r}" for k in values if k not in by]
    for k, fields in values.items():
        for f in fields:
            base = f.rstrip("+")
            if base not in col:
                problems.append(f"{k}: no column for field {base!r}")
            elif base in PROTECTED:
                problems.append(f"{k}: field {base!r} cannot be set here")
    if problems:
        raise ValueError("; ".join(problems))
    wb = openpyxl.load_workbook(workbook)
    ws = wb["vokabular"]
    n = 0
    for k, fields in values.items():
        c = by[k]
        for f, val in fields.items():
            base = f.rstrip("+")
            if f.endswith("+"):
                old = (c.get(base) or "").strip()
                val = f"{old} {val}".strip() if old else val
            ws.cell(c.row, col[base]).value = val
            n += 1
    fit_table(wb)
    apply_formulas(wb)
    wb.save(out or workbook)
    return {"concepts": len(values), "cells": n}

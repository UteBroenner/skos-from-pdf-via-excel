"""Prepare a filled-in v8 workbook: generate what people and the AI extraction should not type.

1. IDs (column A): every row with content but no ID gets the next free <kortnavn>-NNNN.
   IDs are values, not formulas, so sorting or inserting rows never changes them.
   Numbers continue after the highest existing one (a deleted last ID can be reused; keep
   deleted rows with status 'forkastet' instead of removing them).
2. Concept names (column B) for rows without one (see vocabtool.uri).
3. Relations (broader, isPartOf, related): values written as a concept name (column B) or as the
   main-language term are replaced by the concept's ID. Unknown or ambiguous values are left as
   written and reported.
4. Fingerprint (column 'fingeravtrykk', inside the table): SHA-256 of the row content, used by the
   Power Automate import to stamp dato_sist_endret / sist_endret_av only on rows that changed
   (see vocabtool.fingerprint).
5. Excel table, formatting and validation stretched to all rows (see template_ext.fit_table).
"""
from __future__ import annotations

import re

import openpyxl

from .reader import read_workbook, RELATION_FIELDS, split_multi
from .template_ext import uri_as_value, fit_table, ensure_fingerprint_column
from .fingerprint import fingerprint, row_values
from .uri import assign_names


def prepare(path: str) -> dict:
    v = read_workbook(path)
    if v.version != "v8":
        raise ValueError("prepare expects a v8 workbook")
    if not v.kortnavn:
        raise ValueError("kortnavn (scheme cell) is empty")
    wb = openpyxl.load_workbook(path)
    uri_as_value(wb)
    ws = wb["vokabular"]
    cols = {f: openpyxl.utils.column_index_from_string(L) for f, L in v.columns["vokabular"].items()}
    id_re = re.compile(rf"^{re.escape(v.kortnavn)}-(\d{{4}})$")

    # 1. IDs
    used = [int(m.group(1)) for c in v.concepts if (m := id_re.match(c.get("identifier") or ""))]
    nxt = max(used, default=0) + 1
    new_ids = {}
    for c in v.concepts:
        if not c.get("identifier"):
            new = f"{v.kortnavn}-{nxt:04d}"
            nxt += 1
            ws.cell(c.row, cols["identifier"]).value = new
            new_ids[c.key] = new
            c.fields["identifier"] = new
            c.key = new

    # 2. names in column B (before relations, so relations may use the new names)
    names = assign_names(v.concepts, v.label_field, main_lang=v.main_lang)
    collisions = names.pop("_collisions")
    for c in v.concepts:
        if c.key in names:
            ws.cell(c.row, cols.get("uri", 2)).value = names[c.key]
            c.fields["uri"] = names[c.key]

    # 3. relations: name or main-language term -> ID
    lookup = {}
    for c in v.concepts:
        for k in (c.get("uri"), c.get(v.label_field)):
            if k:
                lookup.setdefault(k.strip().lower(), set()).add(c.key)
    ids = {c.key for c in v.concepts}
    converted, unresolved, ambiguous = 0, [], []
    for c in v.concepts:
        for fld in RELATION_FIELDS:
            if fld not in cols or not c.get(fld):
                continue
            out = []
            for t in split_multi(c.get(fld)):
                if t in ids:
                    out.append(t)
                    continue
                hits = lookup.get(t.lower(), set())
                if len(hits) == 1:
                    out.append(next(iter(hits)))
                    converted += 1
                else:
                    out.append(t)
                    (ambiguous if hits else unresolved).append((c.key, fld, t))
            ws.cell(c.row, cols[fld]).value = ", ".join(out)


    # 4. table / formatting, then 5. fingerprints over the final row content
    fp_col = ensure_fingerprint_column(wb)
    fit = fit_table(wb)
    hdr = next(r for r in range(1, 40) if (ws.cell(r, 1).value or "").strip() == "dct:identifier")
    last_col = openpyxl.utils.column_index_from_string(fit["last_column"])
    fp_idx = openpyxl.utils.column_index_from_string(fp_col)
    changed_fp = 0
    for r in range(hdr + 2, ws.max_row + 1):
        if not ws.cell(r, 1).value:
            continue
        fp = fingerprint(row_values(ws, r, hdr + 1, last_col))
        if ws.cell(r, fp_idx).value != fp:
            ws.cell(r, fp_idx).value = fp
            changed_fp += 1
    wb.save(path)
    return {"new_ids": len(new_ids), "relations_converted": converted, "unresolved": unresolved,
            "ambiguous": ambiguous, "new_names": len(names), "name_collisions": collisions, "table": fit,
            "fingerprint_column": fp_col, "fingerprints_updated": changed_fp}

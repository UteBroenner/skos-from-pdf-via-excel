"""Migrate a v7 workbook into the v8 template.

- Assigns IDs <kortnavn>-0001.. in reading order (sheet by sheet, row by row).
- Keeps the v7 concept name: vok:Rekkverk -> "Rekkverk" in column B (a value, not a formula).
  The full URI is then <ConceptScheme URI>/Rekkverk, e.g. …/vokabular/N101/Rekkverk.
- Rewrites broader / isPartOf / related from v7 prefixed URIs (vok:X) to IDs.
  Targets not found in the workbook are kept unchanged and reported.
- Code lists are not migrated.
- Keeps template formulas (URI, change hash), data validation and hidden rows;
  extends formulas and validation ranges when there are more rows than the template has.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter

from .reader import read_workbook, normalise_header, PROPERTY_MAP, CONTRIBUTOR_FIELDS, RELATION_FIELDS
from .template_ext import uri_as_value

DATE_FIELDS = {"created", "modified", "start_date", "end_date"}
# v7 fields without a v8 column, and where they go
FALLBACK = {"change_note": "version_notes"}


def _v8_columns(ws, hdr_row):
    cols, contrib = {}, 0
    for cell in ws[hdr_row]:
        h = normalise_header(cell.value)
        if h == "dct:contributor":
            if contrib < len(CONTRIBUTOR_FIELDS):
                cols[CONTRIBUTOR_FIELDS[contrib]] = cell.column
            contrib += 1
        elif h in PROPERTY_MAP:
            cols.setdefault(PROPERTY_MAP[h], cell.column)
    return cols


def migrate(src: str | Path, template: str | Path, dst: str | Path, kortnavn: str | None = None,
            title: str | None = None) -> dict:
    v7 = read_workbook(src)
    if v7.version != "v7":
        raise ValueError(f"{src} is not a v7 workbook (detected {v7.version})")
    kortnavn = kortnavn or v7.kortnavn
    if not kortnavn or not re.fullmatch(r"[A-Za-z0-9]{1,4}", kortnavn):
        raise ValueError(f"kortnavn must be 1-4 letters/digits, got {kortnavn!r}; pass --kortnavn")

    wb = openpyxl.load_workbook(template)
    uri_as_value(wb)          # column B holds the URI as a value; hash covers A:AM
    ws = wb["vokabular"]
    hdr = next(r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier")
    first = hdr + 2
    cols = _v8_columns(ws, hdr)
    last_template_row = max(r for r in range(first, ws.max_row + 1)
                            if any(isinstance(c.value, str) and c.value.startswith("=") for c in ws[r]))

    # scheme metadata
    for r in range(1, hdr):
        a = normalise_header(ws.cell(r, 1).value)
        if a.startswith("kortnavn"):
            ws.cell(r, 2).value = kortnavn
        elif a == "dct:title":
            ws.cell(r, 2).value = title or v7.title
        elif a == "dct:creator" and v7.concepts:
            pass

    id_of = {c.key: f"{kortnavn}-{i:04d}" for i, c in enumerate(v7.concepts, start=1)}
    unresolved, fallback_used, dropped = [], 0, set()

    # clear example rows
    for r in range(first, last_template_row + 1):
        for f, col in cols.items():
            ws.cell(r, col).value = None

    for i, c in enumerate(v7.concepts):
        r = first + i
        rec = dict(c.fields)
        for f7, f8 in FALLBACK.items():
            if rec.get(f7):
                extra = rec.pop(f7)
                rec[f8] = f"{rec[f8]} | {extra}" if rec.get(f8) else extra
                fallback_used += 1
        rec["identifier"] = id_of[c.key]
        rec["uri"] = c.key.split(":", 1)[-1]   # vok:Rekkverk -> Rekkverk (column B holds the name only)
        for fld in RELATION_FIELDS:
            new = []
            for t in c.relations[fld]:
                if t in id_of:
                    new.append(id_of[t])
                else:
                    new.append(t)
                    unresolved.append((id_of[c.key], fld, t))
            rec[fld] = ", ".join(new) if new else None
        m = re.fullmatch(r'"([^"]*)"@\w+', (rec.get("status") or "").strip())
        if m:
            rec["status"] = m.group(1)
        if c.tier:
            rec["tier"] = int(c.tier) if c.tier.isdigit() else c.tier
        for f, val in rec.items():
            if val is None:
                continue
            if f not in cols:
                dropped.add(f)
                continue
            if f in DATE_FIELDS and isinstance(val, str):
                try:
                    val = datetime.fromisoformat(val[:10])
                except ValueError:
                    pass
            ws.cell(r, cols[f]).value = val
            if f in DATE_FIELDS and isinstance(val, datetime):
                ws.cell(r, cols[f]).number_format = "yyyy-mm-dd"

    # extend formulas (URI col B, hash col) and validations beyond template rows
    n_last = first + len(v7.concepts) - 1
    hash_col = next((c.column for c in ws[hdr + 1] if normalise_header(c.value) == "endringshash"), None)
    for r in range(last_template_row + 1, n_last + 1):
        if hash_col:
            ws.cell(r, hash_col).value = (f'=IF(ISBLANK(vokabular!$A{r}),"",_xlfn.TEXTJOIN("|",FALSE,'
                                          f'vokabular!$A{r}:$AM{r}))')
    if n_last > last_template_row:
        for dv in ws.data_validations.dataValidation:
            new_ranges = []
            for rng in str(dv.sqref).split():
                new_ranges.append(re.sub(rf"(\$?){last_template_row}$", rf"\g<1>{n_last}", rng))
            dv.sqref = openpyxl.worksheet.cell_range.MultiCellRange(" ".join(new_ranges))
            if dv.formula1 and f"${last_template_row}" in dv.formula1:
                dv.formula1 = dv.formula1.replace(f"${last_template_row}", f"${n_last}")

    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    return {
        "source": str(src), "target": str(dst), "kortnavn": kortnavn,
        "concepts": len(v7.concepts), "rows": f"{first}-{n_last}",
        "unresolved_relations": unresolved,
        "change_note_moved_to_version_notes": fallback_used,
        "fields_without_v8_column": sorted(dropped),
        "id_map": id_of,
    }

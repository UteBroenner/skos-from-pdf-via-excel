"""Migrate a v7 workbook into the v8 template.

- Column A (dct:identifier) is the template formula <kortnavn>-<concept name>.
- Keeps the v7 concept name: vok:Rekkverk -> "Rekkverk" in column B (a value, not a formula).
  The full URI is then <ConceptScheme URI>/Rekkverk, e.g. …/vokabular/N101/Rekkverk.
- Rewrites broader / isPartOf / related from v7 prefixed URIs (vok:X) to concept names (X).
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
from .template_ext import uri_as_value, fit_table, apply_formulas

DATE_FIELDS = {"created", "modified", "start_date", "end_date"}
# v7 fields without a v8 column, and where they go
FALLBACK = {"change_note": "version_notes"}


_PREFIX_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*:(?=\S)")


def _strip_prefix(key: str) -> str:
    """vok:Rekkverk -> Rekkverk. Text with a colon followed by a space ("Skadekonsekvens for: bæreevne")
    is not a prefixed name and is kept whole; so are full URIs (http://...)."""
    key = key.strip()
    if key.lower().startswith(("http://", "https://", "urn:")):
        return key
    return _PREFIX_RE.sub("", key, count=1)


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
    if not kortnavn or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", kortnavn):
        raise ValueError(f"kortnavn must be letters, digits or hyphens, got {kortnavn!r}; pass --kortnavn")

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

    name_of = {c.key: _strip_prefix(c.key) for c in v7.concepts}   # vok:Rekkverk -> Rekkverk
    unresolved, fallback_used, dropped = [], 0, set()

    # clear example rows (keep template formulas)
    for r in range(first, last_template_row + 1):
        for f, col in cols.items():
            v = ws.cell(r, col).value
            if not (isinstance(v, str) and v.startswith("=")):
                ws.cell(r, col).value = None

    for i, c in enumerate(v7.concepts):
        r = first + i
        rec = dict(c.fields)
        for f7, f8 in FALLBACK.items():
            if rec.get(f7):
                extra = rec.pop(f7)
                rec[f8] = f"{rec[f8]} | {extra}" if rec.get(f8) else extra
                fallback_used += 1
        rec["identifier"] = None                 # column A: template formula <kortnavn>-<name>
        rec["uri"] = name_of[c.key]              # column B holds the name only
        for fld in RELATION_FIELDS:
            new = []
            for t in c.relations[fld]:
                if t in name_of:
                    new.append(name_of[t])
                else:
                    new.append(_strip_prefix(t))
                    unresolved.append((name_of[c.key], fld, t))
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
            cur = ws.cell(r, cols[f]).value
            if isinstance(cur, str) and cur.startswith("="):
                continue           # template formula (e.g. opprettet_av = dct:creator) wins
            ws.cell(r, cols[f]).value = val
            if f in DATE_FIELDS and isinstance(val, datetime):
                ws.cell(r, cols[f]).number_format = "yyyy-mm-dd"

    # extend formulas (URI col B, hash col) and validations beyond template rows
    n_last = first + len(v7.concepts) - 1
    hash_col = next((c.column for c in ws[hdr + 1] if normalise_header(c.value) == "endringshash"), None)
    # copy every formula of the last template row (change hash, opprettet_av = dct:creator, …) to the new rows
    template_formulas = {c.column: c.value for c in ws[last_template_row]
                         if isinstance(c.value, str) and c.value.startswith("=")}
    for r in range(last_template_row + 1, n_last + 1):
        for col, f in template_formulas.items():
            ws.cell(r, col).value = re.sub(rf"(\$?[A-Z]{{1,3}}){last_template_row}\b", rf"\g<1>{r}", f)
    if n_last > last_template_row:
        for dv in ws.data_validations.dataValidation:
            new_ranges = []
            for rng in str(dv.sqref).split():
                new_ranges.append(re.sub(rf"(\$?){last_template_row}$", rf"\g<1>{n_last}", rng))
            dv.sqref = openpyxl.worksheet.cell_range.MultiCellRange(" ".join(new_ranges))
            if dv.formula1 and f"${last_template_row}" in dv.formula1:
                dv.formula1 = dv.formula1.replace(f"${last_template_row}", f"${n_last}")

    fit_table(wb)              # table, formatting and validation cover all rows and columns
    apply_formulas(wb)         # column A = <kortnavn>-<name>, endringshash
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    return {
        "source": str(src), "target": str(dst), "kortnavn": kortnavn,
        "concepts": len(v7.concepts), "rows": f"{first}-{n_last}",
        "unresolved_relations": unresolved,
        "change_note_moved_to_version_notes": fallback_used,
        "fields_without_v8_column": sorted(dropped),
        "name_map": name_of,
    }

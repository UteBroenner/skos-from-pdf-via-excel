"""Value lists of the template (hidden sheet 'lister') and their dropdowns in the vokabular sheet.

The lists are defined here once; the dropdowns, the 'lister' sheet and its named ranges are written from this
definition every time a tool saves a workbook (save_workbook). Reason: openpyxl, which the tools use, drops data
validations stored in Excel's newer extension format when it saves a file.

The dropdowns hold their values directly ("kandidat,gjeldende,utdatert,forkastet"), not a reference to the
'lister' sheet. They work wherever the rows are copied (another workbook, a SharePoint export), and do not break when
the hidden sheet or a named range is removed. The 'lister' sheet documents the codes and URIs behind each label.

The values must match the enums in schema/svv_vokabular.yaml (ConceptStatus, Audience, RelationshipWithSource);
tests/test_lists.py checks this.
"""
from __future__ import annotations

import re
from pathlib import Path

from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

from .reader import normalise_header, audience, source_relation

SHEET = "lister"

# (property in the header row, named range, first column on the 'lister' sheet, headers, rows: label, code, URI)
LISTS = [
    ("euvoc:status", "statusliste", 1, ("status (nb)", "EuVoc-kode", "EuVoc-URI (concept-status)"), [
        ("kandidat", "CANDIDATE", "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"),
        ("gjeldende", "CURRENT", "http://publications.europa.eu/resource/authority/concept-status/CURRENT"),
        ("utdatert", "DEPRECATED", "http://publications.europa.eu/resource/authority/concept-status/DEPRECATED"),
        ("forkastet", "RETIRED", "http://publications.europa.eu/resource/authority/concept-status/RETIRED"),
    ]),
    ("dct:audience", "malgruppeliste", 5, ("målgruppe (nb)", "kode", "URI (audience-type)"), [
        ("allmennheten", "public", "https://data.norge.no/vocabulary/audience-type#public"),
        ("spesialist", "specialist", "https://data.norge.no/vocabulary/audience-type#specialist"),
    ]),
    ("skosno:relationshipWithSource", "kildeforholdliste", 9, ("forhold_til_kilde", "kode", "URI"), [
        ("basert på kilde", "derived-from-source", "https://data.norge.no/vocabulary/relationship-with-source-type#derived-from-source"),
        ("egendefinert", "self-composed", "https://data.norge.no/vocabulary/relationship-with-source-type#self-composed"),
        ("sitat fra kilde", "direct-from-source", "https://data.norge.no/vocabulary/relationship-with-source-type#direct-from-source"),
    ]),
]

# internal column outside the table (not imported): dropdown only, no codes or URIs
TIER = ("tier", ("1", "2", "3"))


def _dropdown(ws, c, first, last, values):
    """Replace any dropdown on column c by one with the given values, for rows first..last."""
    for dv in list(ws.data_validations.dataValidation):
        if any(rng.min_col <= c <= rng.max_col for rng in dv.sqref.ranges):
            ws.data_validations.dataValidation.remove(dv)
    dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True, showDropDown=False,
                        showErrorMessage=True, showInputMessage=True, errorStyle="warning",
                        errorTitle="Verdi utenfor listen", error="Velg en verdi fra listen.")
    letter = get_column_letter(c)
    dv.add(f"{letter}{first}:{letter}{last}")
    ws.add_data_validation(dv)
    return letter


def _to_label(prop, rows, value):
    """The list label for a value the tools recognise (code, other case, nynorsk), else None."""
    v = " ".join(str(value).strip().lower().split())
    if prop == "dct:audience":
        code = audience(v)
    elif prop == "skosno:relationshipWithSource":
        code = source_relation(v)
    else:
        code = next((c for label, c, _ in rows if v in (label, c.lower())), None)
    return next((label for label, c, _ in rows if c == code), None)


def _header_row(ws):
    return next((r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier"), None)


def ensure_lists(wb, sheet: str = "vokabular") -> list[str]:
    """Write the 'lister' sheet, the named ranges and the dropdowns (data rows of the Excel table).

    Values the tools recognise are written as the list label, e.g. direct-from-source -> sitat fra kilde,
    basert på kjelde -> basert på kilde, Kandidat -> kandidat, public -> allmennheten, so that they match the
    dropdown and the SharePoint choice columns. Other values are left as they are (the checker reports them).
    Only for workbooks in the current layout (row of technical names under the properties). Returns the columns
    that got a dropdown.
    """
    if sheet not in wb.sheetnames:
        return []
    ws = wb[sheet]
    hdr = _header_row(ws)
    if not hdr or "intern_identifikator" not in [c.value for c in ws[hdr + 1]]:
        return []
    ls = wb[SHEET] if SHEET in wb.sheetnames else wb.create_sheet(SHEET)
    ls.sheet_state = "hidden"
    first = hdr + 2
    ends = [int(re.search(r"(\d+)$", t.ref).group(1)) for t in ws.tables.values()]
    last = max(ends + [ws.max_row, first])
    cols = {normalise_header(c.value): c.column for c in ws[hdr] if c.value}
    done = []
    for prop, name, col0, headers, rows in LISTS:
        for i, h in enumerate(headers):
            ls.cell(1, col0 + i).value = h
        for r, row in enumerate(rows, start=2):
            for i, v in enumerate(row):
                ls.cell(r, col0 + i).value = v
        ref = f"{SHEET}!${get_column_letter(col0)}$2:${get_column_letter(col0)}${len(rows) + 1}"
        if name in wb.defined_names:
            del wb.defined_names[name]
        wb.defined_names[name] = DefinedName(name, attr_text=ref)
        c = cols.get(prop)
        if not c:
            continue
        for r in range(first, last + 1):
            cell = ws.cell(r, c)
            if isinstance(cell.value, str) and cell.value.strip():
                label = _to_label(prop, rows, cell.value)
                if label and label != cell.value:
                    cell.value = label
        done.append(_dropdown(ws, c, first, last, [label for label, _, _ in rows]))
    tier_col = cols.get(TIER[0])
    if tier_col:
        done.append(_dropdown(ws, tier_col, first, last, TIER[1]))
    return done


def save_workbook(wb, path) -> None:
    """Save a workbook after restoring the value lists and dropdowns (see module docstring)."""
    ensure_lists(wb)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)

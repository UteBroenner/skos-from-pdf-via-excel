"""Add language columns (prefLabel / altLabel) to the v8 template.

New columns are appended after the last used column, so existing v8 column
letters (and SharePoint column mappings) stay unchanged. The change-hash
formula is extended to include the new columns.
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter

from .reader import normalise_header

LANG_NAMES_NB = {"en-US": "engelsk_us", "en-GB": "engelsk_gb", "de": "tysk", "es": "spansk",
                 "sv": "svensk", "da": "dansk", "fr": "fransk"}


def lang_field(lang: str) -> str:
    return lang.lower().replace("-", "_")


def extend_template(src: str | Path, dst: str | Path, langs: list[str]) -> list[str]:
    wb = openpyxl.load_workbook(src)
    ws = wb["vokabular"]
    hdr = next(r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier")
    tech, req, desc = hdr + 1, hdr - 3, hdr - 2
    existing = {normalise_header(c.value) for c in ws[hdr]}
    col = ws.max_column + 1
    style_src = ws.cell(hdr, 3)          # prefLabel@nb header as style model
    tech_src = ws.cell(tech, 3)
    added = []
    for kind, prop, nb_prefix, sep in (("pref", "skos:prefLabel", "anbefalt_term", False),
                                       ("alt", "skos:altLabel", "tillat_term", True)):
        for lang in langs:
            header = f"{prop}@{lang}" + (' (separator=",")' if sep else "")
            if normalise_header(header) in existing:
                continue
            letter = get_column_letter(col)
            ws.cell(hdr, col).value = header
            ws.cell(tech, col).value = f"{nb_prefix}_{LANG_NAMES_NB.get(lang, lang_field(lang))}"
            ws.cell(req, col).value = "valgfri"
            ws.cell(desc, col).value = "tillat term [0..n]" if sep else f"anbefalt term ({lang}), maks én"
            for r, src_cell in ((hdr, style_src), (tech, tech_src)):
                ws.cell(r, col)._style = copy.copy(src_cell._style)
            ws.column_dimensions[letter].width = ws.column_dimensions["C"].width or 22
            added.append(f"{letter}: {header}")
            col += 1
    last = get_column_letter(col - 1)
    # extend the change hash (TEXTJOIN over A, C:AM) with the new columns
    for r in range(tech + 1, ws.max_row + 1):
        for c in ws[r]:
            if isinstance(c.value, str) and "TEXTJOIN" in c.value and "$AM" in c.value and ",vokabular!$AP" not in c.value:
                c.value = re.sub(r"(vokabular!\$C(\d+):\$AM\d+)", rf"\1,vokabular!$AP\2:${last}\2", c.value)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    return added

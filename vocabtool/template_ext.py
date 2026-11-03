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


def uri_as_value(wb) -> int:
    """Column B (URI) holds only the concept name instead of the formula B1&"/"&A.

    The change hash (column AN) then covers A:AM, so a changed URI is detected too.
    Returns the number of formulas removed.
    """
    ws = wb["vokabular"]
    hdr = next(r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier")
    removed = 0
    ws.cell(hdr - 2, 2).value = ("begrepsnavn i CamelCase, f.eks. Rekkverk (kun bokstaver og tall); "
                                 "URI = ConceptScheme URI (B1) + / + navnet")
    for r in range(hdr + 2, ws.max_row + 1):
        b = ws.cell(r, 2)
        if isinstance(b.value, str) and b.value.startswith("=") and "$B$1" in b.value:
            b.value = None
            removed += 1
        for c in ws[r]:
            if isinstance(c.value, str) and "TEXTJOIN" in c.value:
                c.value = re.sub(rf"vokabular!\$A{r},vokabular!\$C{r}:", f"vokabular!$A{r}:", c.value)
    return removed


def extend_template(src: str | Path, dst: str | Path, langs: list[str], def_langs: list[str] = (),
                    main_lang: str | None = None, scope_langs: list[str] = ()) -> list[str]:
    wb = openpyxl.load_workbook(src)
    ws = wb["vokabular"]
    hdr = next(r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier")
    tech, req, desc = hdr + 1, hdr - 3, hdr - 2
    existing = {normalise_header(c.value) for c in ws[hdr]}
    col = ws.max_column + 1
    style_src = ws.cell(hdr, 3)          # prefLabel@nb header as style model
    tech_src = ws.cell(tech, 3)
    added = []
    for kind, prop, nb_prefix, sep, kind_langs in (("pref", "skos:prefLabel", "anbefalt_term", False, langs),
                                                   ("alt", "skos:altLabel", "tillat_term", True, langs),
                                                   ("def", "skos:definition", "definisjon", False, def_langs),
                                                   ("scope", "skos:scopeNote", "merknad", False, scope_langs)):
        for lang in kind_langs:
            header = f"{prop}@{lang}" + (' (separator=",")' if sep else "")
            if normalise_header(header) in existing:
                continue
            letter = get_column_letter(col)
            ws.cell(hdr, col).value = header
            ws.cell(tech, col).value = f"{nb_prefix}_{LANG_NAMES_NB.get(lang, lang_field(lang))}"
            ws.cell(req, col).value = "valgfri"
            ws.cell(desc, col).value = ("tillat term [0..n]" if sep else f"definisjon ({lang})" if kind == "def"
                                        else f"merknad om bruk ({lang})" if kind == "scope"
                                        else f"anbefalt term ({lang}), maks én")
            for r, src_cell in ((hdr, style_src), (tech, tech_src)):
                ws.cell(r, col)._style = copy.copy(src_cell._style)
            ws.column_dimensions[letter].width = ws.column_dimensions["C"].width or 22
            added.append(f"{letter}: {header}")
            col += 1
    last = get_column_letter(col - 1)
    # main language row (scheme metadata, the empty row above the requirement row)
    ws.cell(req - 1, 1).value = "hovedspråk"
    ws.cell(req - 1, 2).value = main_lang or "nb"
    ws.cell(req - 1, 4).value = "språk der alle begreper må ha anbefalt term og definisjon (BCP 47, f.eks. nb, en-US)"
    # extend the change hash (TEXTJOIN over A, C:AM) with the new columns
    for r in range(tech + 1, ws.max_row + 1):
        for c in ws[r]:
            if isinstance(c.value, str) and "TEXTJOIN" in c.value and "$AM" in c.value and ",vokabular!$AP" not in c.value:
                c.value = re.sub(r"(vokabular!\$[AC](\d+):\$AM\d+)", rf"\1,vokabular!$AP\2:${last}\2", c.value)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    return added

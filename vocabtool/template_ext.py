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
    desc = ws.cell(hdr - 2, 2)
    if not desc.value or "kortnavn-0001" in str(desc.value):   # only replace the original v8 example text
        desc.value = ("begrepsnavn i CamelCase, f.eks. Rekkverk (kun bokstaver og tall); "
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
    # keep 'tier' (internal, not imported) as the last column, outside the Excel table:
    # new columns are inserted in front of it
    tier_col = next((c.column for c in ws[hdr] if normalise_header(c.value) == "tier"), None)
    n_new = sum(1 for kind_langs in (langs, langs, def_langs, scope_langs) for lang in kind_langs)
    if tier_col and tier_col == max(c.column for c in ws[hdr] if c.value not in (None, "")) and n_new:
        tier_width = ws.column_dimensions[get_column_letter(tier_col)].width
        ws.insert_cols(tier_col, n_new)
        ws.column_dimensions[get_column_letter(tier_col + n_new)].width = tier_width or 10
        col = tier_col
    first_new = get_column_letter(col)
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
            if isinstance(c.value, str) and "TEXTJOIN" in c.value and "$AM" in c.value and f",vokabular!${first_new}" not in c.value:
                c.value = re.sub(r"(vokabular!\$[AC](\d+):\$AM\d+)", rf"\1,vokabular!${first_new}\2:${last}\2", c.value)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    return added


def fit_table(wb, sheet: str = "vokabular") -> dict:
    """Stretch the Excel table, formatting, conditional formatting and data validation
    to the last used row (ID in column A) and the last header column.

    Power Automate reads only rows and columns inside the table, so rows below the
    template's 102 prepared rows, and columns added after AN (tier, language extension),
    must be inside it.
    """
    from copy import copy as _copy
    from openpyxl.styles import Alignment
    from openpyxl.worksheet.table import TableColumn
    from openpyxl.formatting.formatting import ConditionalFormattingList

    ws = wb[sheet]
    hdr = next(r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier")
    tech, first = hdr + 1, hdr + 2
    last_col = max(c.column for c in ws[hdr] if c.value not in (None, ""))
    if normalise_header(ws.cell(hdr, last_col).value) == "tier":
        last_col -= 1          # tier is internal: not in the table, not imported
    # never shrink: last row with an ID, with prepared formulas (template rows), or the current table end
    formula_rows = [r for r in range(first, ws.max_row + 1)
                    if any(isinstance(c.value, str) and c.value.startswith("=") for c in ws[r])]
    table_ends = [int(re.search(r"(\d+)$", t.ref).group(1)) for t in ws.tables.values()]
    last_row = max([r for r in range(first, ws.max_row + 1) if ws.cell(r, 1).value or ws.cell(r, 2).value]
                   + formula_rows + table_ends + [first])
    L = get_column_letter(last_col)

    # every table column needs a unique, non-empty header in the technical-name row
    for col in range(1, last_col + 1):
        if not ws.cell(tech, col).value:
            ws.cell(tech, col).value = normalise_header(ws.cell(hdr, col).value).split(":")[-1].replace("@", "_") or f"kolonne_{col}"
            ws.cell(tech, col)._style = _copy(ws.cell(tech, 3)._style)

    tables = list(ws.tables.values())
    out = {"rows": f"{first}-{last_row}", "last_column": L}
    for t in tables:
        start = t.ref.split(":")[0]
        t.ref = f"{start}:{L}{last_row}"
        if t.autoFilter is not None:
            t.autoFilter.ref = t.ref
        t.tableColumns = [TableColumn(id=i + 1, name=str(ws.cell(tech, col).value))
                          for i, col in enumerate(range(1, last_col + 1))]
        out[t.name] = t.ref

    # formatting: top-aligned, wrapped text in every data cell
    for r in range(first, last_row + 1):
        for col in range(1, last_col + 1):
            c = ws.cell(r, col)
            al = _copy(c.alignment)
            c.alignment = Alignment(horizontal=al.horizontal, vertical="top", wrap_text=True)

    # conditional formatting and data validation down to the last row
    def stretch(ref: str) -> str:
        return " ".join(re.sub(r"(\$?[A-Z]+\$?)(\d+)$", lambda m: m.group(1) + str(max(int(m.group(2)), last_row)), part)
                        if ":" in part else part for part in ref.split())
    old = ws.conditional_formatting
    new = ConditionalFormattingList()
    for cf in old:
        for rule in cf.rules:
            new.add(stretch(str(cf.sqref)), rule)
    ws.conditional_formatting = new
    for dv in ws.data_validations.dataValidation:
        dv.sqref = openpyxl.worksheet.cell_range.MultiCellRange(stretch(str(dv.sqref)))
    return out


def hide_column(wb, technical_name: str, sheet: str = "vokabular") -> str | None:
    """Hide the column whose technical name (row below the property header) matches, e.g. 'opprettet_av'."""
    ws = wb[sheet]
    hdr = next(r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier")
    for c in ws[hdr + 1]:
        if c.value == technical_name:
            ws.column_dimensions[c.column_letter].hidden = True
            return c.column_letter
    return None



HASH_COLUMN = "endringshash"
GOVERNANCE = {"intern_identifikator", "dato_opprettet", "opprettet_av", "dato_sist_endret", "sist_endret_av", HASH_COLUMN}


def _ranges(cols: list[int]) -> list[tuple[int, int]]:
    out = []
    for c in sorted(cols):
        if out and c == out[-1][1] + 1:
            out[-1] = (out[-1][0], c)
        else:
            out.append((c, c))
    return out


def apply_formulas(wb, sheet: str = "vokabular") -> dict:
    """Write the two formula columns for every row of the Excel table:

    - column A (dct:identifier) = <kortnavn>-<concept name>, e.g. N101-Rekkverk
    - endringshash = TEXTJOIN of the row content (all table columns except ID, created/modified
      date and person, and the hash itself); Power Automate compares it with the List to find changed rows.
    The endringshash column is added before a trailing 'tier' if the template has none.
    """
    ws = wb[sheet]
    hdr = next(r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier")
    tech, first = hdr + 1, hdr + 2
    k_row = next(r for r in range(1, hdr) if normalise_header(ws.cell(r, 1).value).startswith("kortnavn"))
    # make sure the hash column exists, inside the table, before a trailing tier
    hash_col = next((c.column for c in ws[tech] if c.value == HASH_COLUMN), None)
    if hash_col is None:
        last = max(c.column for c in ws[hdr] if c.value not in (None, ""))
        hash_col = last + 1
        if normalise_header(ws.cell(hdr, last).value) == "tier":
            width = ws.column_dimensions[get_column_letter(last)].width
            ws.insert_cols(last, 1)
            ws.column_dimensions[get_column_letter(last + 1)].width = width or 10
            hash_col = last
        for r, src in ((hdr, ws.cell(hdr, 3)), (tech, ws.cell(tech, 3)), (hdr - 3, ws.cell(hdr - 3, 3))):
            ws.cell(r, hash_col)._style = copy.copy(src._style)
        ws.cell(hdr, hash_col).value = HASH_COLUMN
        ws.cell(tech, hash_col).value = HASH_COLUMN
        ws.cell(hdr - 3, hash_col).value = "systemgenerert"
        ws.column_dimensions[get_column_letter(hash_col)].width = 20
    ws.cell(hdr - 2, hash_col).value = ("formel: radens innhold uten ID, datoer og personer; brukes av Power Automate "
                                        "for å finne endrede begreper – ikke rediger")
    ws.cell(hdr - 2, 1).value = "genereres: <kortnavn>-<begrepsnavn>, f.eks. N101-Rekkverk – ikke rediger"
    t = next(iter(ws.tables.values()))
    end_col = openpyxl.utils.column_index_from_string(re.match(r"[A-Z]+", t.ref.split(":")[1]).group(0))
    last_row = int(re.search(r"(\d+)$", t.ref).group(1))
    content = [c for c in range(1, end_col + 1) if ws.cell(tech, c).value and ws.cell(tech, c).value not in GOVERNANCE]
    for r in range(first, last_row + 1):
        parts = ",".join(f"${get_column_letter(a)}{r}:${get_column_letter(b)}{r}" if a != b else f"${get_column_letter(a)}{r}"
                         for a, b in _ranges(content))
        ws.cell(r, 1).value = f'=IF(${"B"}{r}="","",$B${k_row}&"-"&$B{r})'
        ws.cell(r, hash_col).value = f'=IF($B{r}="","",_xlfn.TEXTJOIN("|",FALSE,{parts}))'
    return {"rows": f"{first}-{last_row}", "hash_column": get_column_letter(hash_col),
            "hash_covers": ",".join(f"{get_column_letter(a)}:{get_column_letter(b)}" for a, b in _ranges(content))}

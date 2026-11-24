"""Template upkeep: language columns, formulas, the Excel table and header colours.

- extend_template: add language columns (prefLabel, altLabel, definition, scope note); they are inserted in front of
  endringshash, so the columns A–AM keep their letters (and their SharePoint column mappings)
- apply_formulas: the formulas in A (identifier), B (concept name), opprettet_av and endringshash
- fit_table: stretch the Excel table, formatting, conditional formatting and dropdowns to all rows in use
- requirement_colours: colour the header rows of added columns by requirement level
- uri_as_value, hide_column: helpers for migrate and older layouts
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter

from .reader import normalise_header
from .uri import name_formula
from .lists import save_workbook

# language tag -> Norwegian name used in the technical names of added columns
LANG_NAMES_NB = {"en-US": "engelsk_us", "en-GB": "engelsk_gb", "de": "tysk", "es": "spansk",
                 "sv": "svensk", "da": "dansk", "fr": "fransk"}


def lang_field(lang: str) -> str:
    """Field suffix for a language tag: en-US -> en_us."""
    return lang.lower().replace("-", "_")


def uri_as_value(wb) -> int:
    """Remove the old v8 formula B1&"/"&A from column B, so B holds the concept name as a value.

    Used by migrate. Only the original v8 example text in the description row is replaced.

    Returns:
        The number of formulas removed.
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
    """Write a copy of the template with language columns added.

    Columns are inserted in front of endringshash (or the type column), with the style of column C; the description
    row and the row hovedspråk (main language) are filled in. Formulas, table and colours are rebuilt.

    Args:
        src: the template.
        dst: the file to write.
        langs: languages for prefLabel and altLabel columns, e.g. ["en-US", "de"].
        def_langs: languages for definition columns.
        main_lang: value of the row hovedspråk (default nb).
        scope_langs: languages for scope-note columns.

    Returns:
        The columns added, as "<letter>: <header>".
    """
    wb = openpyxl.load_workbook(src)
    ws = wb["vokabular"]
    hdr = next(r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier")
    tech, req, desc = hdr + 1, hdr - 3, hdr - 2
    existing = {normalise_header(c.value) for c in ws[hdr]}
    col = ws.max_column + 1
    # keep 'type' (internal, not imported) as the last column, outside the Excel table:
    # new columns are inserted in front of it
    type_col = next((c.column for c in ws[hdr] if normalise_header(c.value) in TYPE_HEADERS), None)
    hash_col = next((c.column for c in ws[hdr + 1] if c.value == "endringshash"), None)
    n_new = sum(1 for kind_langs in (langs, langs, def_langs, scope_langs) for lang in kind_langs)
    # new columns go in front of endringshash (the last table column) or, without it, in front of type
    at = hash_col or (type_col if type_col and type_col == max(c.column for c in ws[hdr] if c.value not in (None, "")) else None)
    if at and n_new:
        widths = {k: ws.column_dimensions[get_column_letter(k)].width for k in range(at, ws.max_column + 1)}
        ws.insert_cols(at, n_new)
        for k, w in widths.items():
            ws.column_dimensions[get_column_letter(k + n_new)].width = w or 10
        col = at
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
            for r, src_cell in ((hdr, style_src), (tech, tech_src), (desc, ws.cell(desc, 3))):
                ws.cell(r, col)._style = copy.copy(src_cell._style)       # colours follow the level below
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
    new_cols = list(range(openpyxl.utils.column_index_from_string(first_new), col))
    if hash_col:                 # current templates: the table and the formulas are rebuilt
        fit_table(wb)
        apply_formulas(wb)
        new_cols.append(next(c.column for c in ws[tech] if c.value == HASH_COLUMN))
    requirement_colours(wb, columns=new_cols)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    save_workbook(wb, dst)
    return added


def _colour(cell) -> tuple:
    """Fill and font colour of a cell, for comparing colourings."""
    f, fo = cell.fill, cell.font
    fg = f.fgColor if f.fill_type else None
    fc = fo.color
    return (f.fill_type, fg.type if fg else None, (fg.theme if fg.type == "theme" else fg.rgb) if fg else None,
            round(fg.tint or 0, 3) if fg else 0, fo.b,
            (fc.theme if fc.type == "theme" else fc.rgb) if fc else None, round(fc.tint or 0, 3) if fc else 0)


def requirement_colours(wb, sheet: str = "vokabular", columns=None) -> list[str]:
    """Colour the requirement row, the property row and the technical-name row of the given columns
    (column numbers) by the requirement level.

    Only columns the tools add (language columns, endringshash) or name explicitly are coloured: the template's own
    columns keep their colours, which may deliberately differ from the level in the requirement row (e.g. columns
    that are obligatory in Statens vegvesen but optional in SKOS-AP-NO are orange in the technical-name row).

    The level is the text in the requirement row (obligatorisk, anbefalt, valgfri, internt, systemgenerert). For each
    level the colouring the template uses most often for that level is the model. Only fill and font colour (and bold)
    are copied, so the template's own theme (branding) colours are kept and borders, alignment and widths stay as
    they are. systemgenerert is coloured like internt. Columns without a level are left as they are.
    Returns the cells that changed.
    """
    from collections import Counter
    ws = wb[sheet]
    hdr = next(r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier")
    rows = (hdr - 3, hdr, hdr + 1)                     # requirement, property, technical name
    last = max(c.column for c in ws[hdr] if c.value not in (None, ""))
    level = {c: str(ws.cell(hdr - 3, c).value or "").strip().lower() for c in range(1, last + 1)}
    sig = lambda c: tuple(_colour(ws.cell(r, c)) for r in rows)
    model = {}
    for lv in set(level.values()) - {""}:
        cols = [c for c in level if level[c] == lv]
        common = Counter(sig(c) for c in cols).most_common(1)[0][0]
        model[lv] = next(c for c in cols if sig(c) == common)
    if "internt" in model:
        model["systemgenerert"] = model["internt"]
    changed = []
    for c, lv in level.items():
        if columns is not None and c not in columns:
            continue
        m = model.get(lv)
        if not m or m == c:
            continue
        for r in rows:
            src, dst = ws.cell(r, m), ws.cell(r, c)
            if _colour(src) != _colour(dst):
                dst.fill = copy.copy(src.fill)
                font = copy.copy(dst.font)
                font.color, font.b = copy.copy(src.font.color), src.font.b
                dst.font = font
                changed.append(dst.coordinate)
    return changed


def fit_table(wb, sheet: str = "vokabular") -> dict:
    """Stretch the Excel table, formatting, conditional formatting and data validation
    to the last used row (ID in column A) and the last header column.

    Power Automate reads only rows and columns inside the table, so rows below the
    template's 102 prepared rows, and columns added after AN (type, language extension),
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
    if normalise_header(ws.cell(hdr, last_col).value) in TYPE_HEADERS:
        last_col -= 1          # type is internal: not in the table, not imported
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

    # formatting: top-aligned, wrapped text in every data cell; endringshash is not wrapped (its long text would
    # make every row tall) and its column is wide
    hash_col = next((c.column for c in ws[tech] if c.value == HASH_COLUMN), None)
    for r in range(first, last_row + 1):
        for col in range(1, last_col + 1):
            c = ws.cell(r, col)
            al = _copy(c.alignment)
            c.alignment = Alignment(horizontal=al.horizontal, vertical="top", wrap_text=col != hash_col)
    if hash_col:
        dim = ws.column_dimensions[get_column_letter(hash_col)]
        dim.width = max(dim.width or 0, HASH_WIDTH)

    # conditional formatting and data validation down to the last row
    def stretch(ref: str) -> str:
        """A range reference with its last row moved down to the end of the table."""
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



# technical name of the change-hash column (last column of the Excel table)
HASH_COLUMN = "endringshash"
# minimum width of the hash column; its text is not wrapped, so rows stay one line high
HASH_WIDTH = 100
TYPE_HEADERS = ("type", "tier")      # the internal column was called tier before 24 November 2026
# description of the type values, written in the description row of the type column
TYPE_DESCRIPTION = ("1 = fysiske objekter, romlige begreper og målbare egenskaper; 2 = prosesser og tilstander; "
                    "3 = normative krav. Internt, importeres ikke.")
# columns left out of the change hash: ID, dates, persons and the hash itself
GOVERNANCE = {"intern_identifikator", "dato_opprettet", "opprettet_av", "dato_sist_endret", "sist_endret_av", HASH_COLUMN}


def _ranges(cols: list[int]) -> list[tuple[int, int]]:
    """Column numbers as (first, last) runs: [1, 2, 3, 5] -> [(1, 3), (5, 5)]."""
    out = []
    for c in sorted(cols):
        if out and c == out[-1][1] + 1:
            out[-1] = (out[-1][0], c)
        else:
            out.append((c, c))
    return out


def apply_formulas(wb, sheet: str = "vokabular") -> dict:
    """Write the formula columns for every row of the Excel table.

    - column A (dct:identifier) = <kortnavn>-<concept name>, e.g. N101-Rekkverk
    - column B (concept name) = CamelCase of the bokmål term (uri.name_formula), where B is empty or already a
      formula; a name typed into B is kept
    - opprettet_av = the scheme's dct:creator (B16), for rows with a concept name
    - endringshash = TEXTJOIN of the row content (all table columns except ID, dates and persons); Power Automate
      compares it with the List to find changed rows

    The endringshash column is added in front of a trailing type column if the template has none. The type header
    is written as "type" (former name: tier) with the description of types 1, 2 and 3.

    Returns:
        rows, hash_column and the columns the hash covers.
    """
    ws = wb[sheet]
    hdr = next(r for r in range(1, 40) if normalise_header(ws.cell(r, 1).value) == "dct:identifier")
    tech, first = hdr + 1, hdr + 2
    k_row = next(r for r in range(1, hdr) if normalise_header(ws.cell(r, 1).value).startswith("kortnavn"))
    # make sure the hash column exists, inside the table, before a trailing type
    hash_col = next((c.column for c in ws[tech] if c.value == HASH_COLUMN), None)
    if hash_col is None:
        last = max(c.column for c in ws[hdr] if c.value not in (None, ""))
        hash_col = last + 1
        if normalise_header(ws.cell(hdr, last).value) in TYPE_HEADERS:
            width = ws.column_dimensions[get_column_letter(last)].width
            ws.insert_cols(last, 1)
            ws.column_dimensions[get_column_letter(last + 1)].width = width or 10
            hash_col = last
        model = hash_col + 1 if normalise_header(ws.cell(hdr, hash_col + 1).value) in TYPE_HEADERS else 3
        for r in (hdr, tech, hdr - 3, hdr - 2):     # systemgenerert: same style as the internal type column
            ws.cell(r, hash_col)._style = copy.copy(ws.cell(r, model)._style)
        ws.cell(hdr, hash_col).value = HASH_COLUMN
        ws.cell(tech, hash_col).value = HASH_COLUMN
        ws.cell(hdr - 3, hash_col).value = "systemgenerert"
        ws.column_dimensions[get_column_letter(hash_col)].width = 20
        fit_table(wb, sheet)       # the new column must be inside the Excel table, or Power Automate does not see it
    ws.cell(hdr - 2, hash_col).value = ("formel: radens innhold uten ID, datoer og personer; brukes av Power Automate "
                                        "for å finne endrede begreper – ikke rediger")
    ws.cell(hdr - 2, 1).value = "genereres: <kortnavn>-<begrepsnavn>, f.eks. N101-Rekkverk – ikke rediger"
    type_col = next((c.column for c in ws[hdr] if normalise_header(c.value) in TYPE_HEADERS), None)
    if type_col:
        ws.cell(hdr, type_col).value = "type"              # former name: tier
        ws.cell(hdr - 2, type_col).value = TYPE_DESCRIPTION
        dim = ws.column_dimensions[get_column_letter(type_col)]
        dim.width = max(dim.width or 0, 30)
    t = next(iter(ws.tables.values()))
    end_col = openpyxl.utils.column_index_from_string(re.match(r"[A-Z]+", t.ref.split(":")[1]).group(0))
    last_row = int(re.search(r"(\d+)$", t.ref).group(1))
    content = [c for c in range(1, end_col + 1) if ws.cell(tech, c).value and ws.cell(tech, c).value not in GOVERNANCE]
    label_col = next((c.column for c in ws[hdr] if normalise_header(c.value) == "skos:prefLabel@nb"), None)
    creator_col = next((c.column for c in ws[tech] if c.value == "opprettet_av"), None)
    creator_row = next((r for r in range(1, hdr) if normalise_header(ws.cell(r, 1).value) == "dct:creator"), None)
    for r in range(first, last_row + 1):
        parts = ",".join(f"${get_column_letter(a)}{r}:${get_column_letter(b)}{r}" if a != b else f"${get_column_letter(a)}{r}"
                         for a, b in _ranges(content))
        ws.cell(r, 1).value = f'=IF(${"B"}{r}="","",$B${k_row}&"-"&$B{r})'
        b = ws.cell(r, 2)
        if label_col and (b.value is None or (isinstance(b.value, str) and b.value.startswith("="))):
            b.value = name_formula(f"{get_column_letter(label_col)}{r}")      # a typed name is kept
        if creator_col and creator_row:
            ws.cell(r, creator_col).value = f'=IF($B{r}="","",$B${creator_row})'
        ws.cell(r, hash_col).value = f'=IF($B{r}="","",_xlfn.TEXTJOIN("|",FALSE,{parts}))'
    return {"rows": f"{first}-{last_row}", "hash_column": get_column_letter(hash_col),
            "hash_covers": ",".join(f"{get_column_letter(a)}:{get_column_letter(b)}" for a, b in _ranges(content))}

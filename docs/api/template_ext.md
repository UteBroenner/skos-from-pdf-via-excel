# `vocabtool.template_ext`

Source: [`vocabtool/template_ext.py`](../../vocabtool/template_ext.py)

Template upkeep: language columns, formulas, the Excel table and header colours.

- extend_template: add language columns (prefLabel, altLabel, definition, scope note); they are inserted in front of
  endringshash, so the columns A–AM keep their letters (and their SharePoint column mappings)
- apply_formulas: the formulas in A (identifier), B (concept name), opprettet_av and endringshash
- fit_table: stretch the Excel table, formatting, conditional formatting and dropdowns to all rows in use
- requirement_colours: colour the header rows of added columns by requirement level
- uri_as_value, hide_column: helpers for migrate and older layouts

## Constants

| Name | Meaning |
| --- | --- |
| `LANG_NAMES_NB` | language tag -> Norwegian name used in the technical names of added columns |
| `HASH_COLUMN` | technical name of the change-hash column (last column of the Excel table) |
| `HASH_WIDTH` | minimum width of the hash column; its text is not wrapped, so rows stay one line high |
| `TYPE_HEADERS` | the internal column was called tier before 24 November 2026 |
| `TYPE_DESCRIPTION` | description of the type values, written in the description row of the type column |
| `GOVERNANCE` | columns left out of the change hash: ID, dates, persons and the hash itself |

## Functions

### `lang_field`

```python
def lang_field(lang: str) -> str
```

Field suffix for a language tag: en-US -> en_us.

### `uri_as_value`

```python
def uri_as_value(wb) -> int
```

Remove the old v8 formula B1&"/"&A from column B, so B holds the concept name as a value.

Used by migrate. Only the original v8 example text in the description row is replaced.

**Returns**

The number of formulas removed.

### `extend_template`

```python
def extend_template(src: str | Path, dst: str | Path, langs: list[str], def_langs: list[str]=(), main_lang: str | None=None, scope_langs: list[str]=()) -> list[str]
```

Write a copy of the template with language columns added.

Columns are inserted in front of endringshash (or the type column), with the style of column C; the description
row and the row hovedspråk (main language) are filled in. Formulas, table and colours are rebuilt.

**Args**

- `src`: the template.
- `dst`: the file to write.
- `langs`: languages for prefLabel and altLabel columns, e.g. ["en-US", "de"].
- `def_langs`: languages for definition columns.
- `main_lang`: value of the row hovedspråk (default nb).
- `scope_langs`: languages for scope-note columns.

**Returns**

The columns added, as "<letter>: <header>".

### `requirement_colours`

```python
def requirement_colours(wb, sheet: str='vokabular', columns=None) -> list[str]
```

Colour the requirement row, the property row and the technical-name row of the given columns
(column numbers) by the requirement level.

Only columns the tools add (language columns, endringshash) or name explicitly are coloured: the template's own
columns keep their colours, which may deliberately differ from the level in the requirement row (e.g. columns
that are obligatory in Statens vegvesen but optional in SKOS-AP-NO are orange in the technical-name row).

The level is the text in the requirement row (obligatorisk, anbefalt, valgfri, internt, systemgenerert). For each
level the colouring the template uses most often for that level is the model. Only fill and font colour (and bold)
are copied, so the template's own theme (branding) colours are kept and borders, alignment and widths stay as
they are. systemgenerert is coloured like internt. Columns without a level are left as they are.
Returns the cells that changed.

### `fit_table`

```python
def fit_table(wb, sheet: str='vokabular') -> dict
```

Stretch the Excel table, formatting, conditional formatting and data validation
to the last used row (ID in column A) and the last header column.

Power Automate reads only rows and columns inside the table, so rows below the
template's 102 prepared rows, and columns added after AN (type, language extension),
must be inside it.

### `hide_column`

```python
def hide_column(wb, technical_name: str, sheet: str='vokabular') -> str | None
```

Hide the column whose technical name (row below the property header) matches, e.g. 'opprettet_av'.

### `apply_formulas`

```python
def apply_formulas(wb, sheet: str='vokabular') -> dict
```

Write the formula columns for every row of the Excel table.

- column A (dct:identifier) = <kortnavn>-<concept name>, e.g. N101-Rekkverk
- column B (concept name) = CamelCase of the bokmål term (uri.name_formula), where B is empty or already a
  formula; a name typed into B is kept
- opprettet_av = the scheme's dct:creator (B16), for rows with a concept name
- endringshash = TEXTJOIN of the row content (all table columns except ID, dates and persons); Power Automate
  compares it with the List to find changed rows

The endringshash column is added in front of a trailing type column if the template has none. The type header
is written as "type" (former name: tier) with the description of types 1, 2 and 3.

**Returns**

rows, hash_column and the columns the hash covers.

## Internal helpers

Documented in the source: `_colour`, `_ranges`.

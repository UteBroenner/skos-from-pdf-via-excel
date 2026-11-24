# `vocabtool.reader`

Source: [`vocabtool/reader.py`](../../vocabtool/reader.py)

Read SKOS vocabulary workbooks (template v7, v8 and v9) into plain records.

Code lists (the `kodeverk` sheet) are deliberately ignored.

## Constants

| Name | Meaning |
| --- | --- |
| `PROPERTY_MAP` | Normalised header (property) -> canonical field name. Headers are normalised by removing whitespace and any "(separator=...)" suffix. |
| `TECHNICAL_NAME_MAP` | columns whose property row holds no property (v8/v9): mapped by the technical name in the row below AB: a prov:Person, written as a name |
| `CONTRIBUTOR_FIELDS` | dct:contributor: v8 has it twice (AD created by, AF modified by), v7 once (created by), v9 once (AF; AD is dct:creator). Each occurrence takes the first of these fields not yet mapped. |
| `SCHEME_BASE` | template v8/v9 cell B1: CONCAT(SCHEME_BASE, kortnavn) |
| `RELATION_FIELDS` | relation fields (concept names, comma-separated) -> SKOS / XKOS property |
| `EXCLUDED_SHEETS` | sheets that hold no concepts: code lists (not processed yet) and the value lists |
| `CURRENT` | template versions with the current column layout (v9 = v8 + value lists on the sheet 'lister') |
| `AUDIENCE_VALUES` | dct:audience: audience-type code (data.norge.no) for the bokmål list value or the code |
| `SOURCE_RELATION_VALUES` | skosno:relationshipWithSource: SKOS-AP-NO code for every way the template allows to write it (English code with hyphens or spaces, bokmål, nynorsk) |

## class `Concept`

One row of the vokabular sheet.

**Attributes**

- `key`: the row key used by relations: the concept name in column B (v8/v9) or the prefixed URI (v7).
- `sheet`: sheet name.
- `row`: row number in the sheet (1-based, as in Excel).
- `fields`: canonical field name -> cell text (see PROPERTY_MAP), e.g. label_nb, def_nb, broader.
- `relations`: relation field (broader, is_part_of, related) -> list of target keys.

### `Concept.get`: `get(self, name, default=None)`

Field value by canonical name, like dict.get.

### `Concept.type` (property)

The type column as text: "1", "2" or "3" (a stored 2.0 becomes "2"); None when empty.

## class `Vocabulary`

A workbook as read by read_workbook.

**Attributes**

- `path`: the workbook file.
- `version`: "v9" (v8 columns plus the sheet lister), "v8", "v7" or "unknown".
- `kortnavn`: short name of the vocabulary (cell B14 in v8/v9), e.g. N101.
- `title`: dct:title of the scheme.
- `scheme_uri`: ConceptScheme URI, http://example.org/vegvesen/vokabular/<kortnavn>.
- `concepts`: the concepts in workbook order.
- `columns`: sheet -> {canonical field: column letter}.
- `unmapped_headers`: sheet -> headers that map to no field.
- `main_lang`: the scheme row "hovedspråk" (default nb); label and definition checks use it.

### `Vocabulary.current` (property)

Current column layout (v8 or v9).

### `Vocabulary.label_field` (property)

Field of the main-language prefLabel, e.g. label_nb or label_en_us.

### `Vocabulary.def_field` (property)

Field of the main-language definition, e.g. def_nb.

### `Vocabulary.by_key`: `by_key(self) -> dict[str, Concept]`

{row key: Concept}.

## Functions

### `lang_column_field`

```python
def lang_column_field(header: str) -> str | None
```

Field name for a language-tagged label/definition column not in PROPERTY_MAP,
e.g. skos:prefLabel@en-US -> label_en_us.

### `field_for`

```python
def field_for(kind: str, lang: str) -> str
```

field_for("label", "en-US") -> "label_en_us".

### `label_fields`

```python
def label_fields(fields) -> dict[str, str]
```

{field: language tag} for all prefLabel/altLabel fields present.

### `audience`

```python
def audience(value)
```

'Allmennheten', 'spesialist', 'public' -> audience-type code; None if not recognised.

### `source_relation`

```python
def source_relation(value)
```

'derived from source', 'Basert på kilde', 'sitat frå kjelde' -> SKOS-AP-NO code; None if not recognised.

### `normalise_header`

```python
def normalise_header(value) -> str
```

Header text without whitespace, a "(separator=...)" suffix or a trailing "?".

Example: 'skos:altLabel @nb (separator=",")' -> 'skos:altLabel@nb'.

### `split_multi`

```python
def split_multi(value) -> list[str]
```

Split a multi-value cell at commas, semicolons and line breaks; empty parts are dropped.

### `as_text`

```python
def as_text(value)
```

Cell value as stripped text (dates as ISO 8601, YYYY-MM-DD); None for empty cells.

### `read_workbook`

```python
def read_workbook(path: str | Path) -> Vocabulary
```

Read a vocabulary workbook (template v7, v8 or v9) into a Vocabulary.

Sheets named kodeverk or lister are skipped. A row counts as a concept if it has an ID, a concept name, or any
label or definition. Formula columns saved by the tools have no cached value, so the concept name (column B) and
the identifier (column A) are computed from the term and kortnavn in the same way as the template formulas.

**Args**

- `path`: the .xlsx file.

**Returns**

The Vocabulary.

## Internal helpers

Documented in the source: `_find_header_row`, `_scheme_meta`.

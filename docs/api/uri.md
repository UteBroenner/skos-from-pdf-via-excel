# `vocabtool.uri`

Source: [`vocabtool/uri.py`](../../vocabtool/uri.py)

Readable concept URIs: <ConceptScheme URI>/<LocalName>.

Column B of template v9 holds only the local name (e.g. "Rekkverk"); the full URI is
the ConceptScheme URI (cell B1) + "/" + the name, put together by the tools.

The local name is the main-language prefLabel in CamelCase, transliterated to
ASCII (ø -> o, æ -> ae, å -> always aa). Acronyms (words written fully in capitals) stay
in capitals. Examples: "brystningshøyde" -> "Brystningshoyde", "skråstagbru" -> "Skraastagbru",
"CE-merket produkt" -> "CEMerketProdukt", "single crochet" -> "SingleCrochet". Clashes between languages (US double crochet = UK treble crochet) are
documented in scope notes, not in the name.

## Constants

| Name | Meaning |
| --- | --- |
| `LOCAL_NAME_RE` | CamelCase concept name: letters and digits only |
| `NAME_WORDS` | Column B (concept name) can be a formula over column C (main-language term). The formula follows local_name: transliteration, words split at spaces and punctuation, each word capitalised with the rest lower case, words written fully in capitals (acronyms) kept. Excel 365/2021 (LET). Up to NAME_WORDS words; a name typed into B replaces the formula. |

## Functions

### `ascii_fold`

```python
def ascii_fold(text: str) -> str
```

Transliterate to ASCII: æ -> ae, ø -> o, å -> aa, ä -> ae, ö -> oe, ü -> ue, ß -> ss; other accents dropped.

### `local_name`

```python
def local_name(label: str) -> str
```

CamelCase local name from a term: each word capitalised, the rest lowercased,
except acronyms (all capitals, e.g. CE, IP, NIB), which are kept as written.

### `local_part`

```python
def local_part(uri: str, scheme_uri: str | None) -> str | None
```

'…/N101/Rekkverk' -> 'Rekkverk' if the URI is under the scheme URI, else None.

### `expected_name`

```python
def expected_name(c, label_field: str) -> str
```

Name the generator would give: CamelCase of the main-language term.

### `concept_uri`

```python
def concept_uri(scheme_uri: str, name: str) -> str
```

<ConceptScheme URI>/<name>.

### `assign_names`

```python
def assign_names(concepts, label_field: str, overwrite: bool=False, main_lang: str='nb') -> dict
```

Return {concept key: local name} for concepts without a name in column B (or all, with overwrite).

Collisions get a numeric suffix (Name2, Name3 …) and are listed under "_collisions".

### `name_formula`

```python
def name_formula(label_cell: str) -> str
```

Excel formula (file syntax) that makes the concept name from the term in label_cell, e.g. 'C25'.

### `name_formula_python`

```python
def name_formula_python(label: str) -> str
```

The formula's logic in Python, to compare with local_name.

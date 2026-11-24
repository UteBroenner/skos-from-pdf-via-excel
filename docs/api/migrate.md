# `vocabtool.migrate`

Source: [`vocabtool/migrate.py`](../../vocabtool/migrate.py)

Migrate a v7 workbook into the v9 template.

- Column A (dct:identifier) is the template formula <kortnavn>-<concept name>.
- Keeps the v7 concept name: vok:Rekkverk -> "Rekkverk" in column B (a value, replacing the template's name formula;
  empty rows keep the formula, so new concepts get their name from the term).
  The full URI is then <ConceptScheme URI>/Rekkverk, e.g. …/vokabular/N101/Rekkverk.
- Rewrites broader / isPartOf / related from v7 prefixed URIs (vok:X) to concept names (X).
  Targets not found in the workbook are kept unchanged and reported.
- Code lists are not migrated.
- Keeps template formulas (URI, change hash), data validation and hidden rows;
  extends formulas and validation ranges when there are more rows than the template has.

## Constants

| Name | Meaning |
| --- | --- |
| `DATE_FIELDS` | fields written as dates |
| `FALLBACK` | v7 fields without a v9 column, and where they go |

## Functions

### `migrate`

```python
def migrate(src: str | Path, template: str | Path, dst: str | Path, kortnavn: str | None=None, title: str | None=None) -> dict
```

Copy a v7 workbook into the v9 template.

The v7 concept names are kept in column B (vok:Rekkverk -> Rekkverk); relations become names; skos:changeNote
moves to adms:versionNotes; dct:creator is copied to the scheme rows. Only real v7 files are accepted.

**Args**

- `src`: the v7 workbook.
- `template`: the v9 template.
- `dst`: the workbook to write.
- `kortnavn`: short name (letters, digits, hyphens); default: from the v7 scheme URI.
- `title`: dct:title; default: from the v7 workbook.

**Returns**

A report dict: concepts, target, rows, kortnavn, name_map, unresolved_relations, fields_without_column, change_note_moved_to_version_notes.

**Raises**

- `ValueError`: the source is not v7, or kortnavn is missing or invalid.

## Internal helpers

Documented in the source: `_strip_prefix`, `_v7_scheme_value`, `_template_columns`.

# `vocabtool.set_fields`

Source: [`vocabtool/set_fields.py`](../../vocabtool/set_fields.py)

Write reviewed values into concepts of a v9 workbook, by concept name (column B).

Input JSON: {"<concept name>": {"<field>": "<value>", ...}, ...}
Fields are the reader's field names (def_nb, source, relationship_with_source, editorial_note, scope_note, ...).
A field name ending in "+" appends to the current value, separated by a space (e.g. "editorial_note+").
Unknown concept names or fields are refused before anything is written. Formula columns are never written.

## Constants

| Name | Meaning |
| --- | --- |
| `PROTECTED` | fields set-fields does not write: formulas and the concept name (use rename) |

## Functions

### `set_fields`

```python
def set_fields(workbook, values: dict | str | Path, out=None) -> dict
```

Write reviewed values into concepts by concept name.

**Args**

- `workbook`: the workbook.
- `values`: {concept name: {field: value}} or a JSON file with it. A field name ending in "+" appends to the cell (with a space) instead of replacing it. Protected fields (identifier, change hash, opprettet_av, concept name) cannot be set.
- `out`: the workbook to write; default: in place.

**Returns**

Counts: cells, concepts.

**Raises**

- `ValueError`: unknown concept names, unknown fields or protected fields (nothing is written).

# `vocabtool.lists`

Source: [`vocabtool/lists.py`](../../vocabtool/lists.py)

Value lists of the template (hidden sheet 'lister') and their dropdowns in the vokabular sheet.

The lists are defined here once; the dropdowns, the 'lister' sheet and its named ranges are written from this
definition every time a tool saves a workbook (save_workbook). Reason: openpyxl, which the tools use, drops data
validations stored in Excel's newer extension format when it saves a file.

The dropdowns hold their values directly ("kandidat,gjeldende,utdatert,forkastet"), not a reference to the
'lister' sheet. They work wherever the rows are copied (another workbook, a SharePoint export), and do not break when
the hidden sheet or a named range is removed. The 'lister' sheet documents the codes and URIs behind each label.

The values must match the enums in schema/svv_vokabular.yaml (ConceptStatus, Audience, RelationshipWithSource);
tests/test_lists.py checks this.

## Constants

| Name | Meaning |
| --- | --- |
| `SHEET` | name of the hidden sheet with the value lists |
| `LISTS` | (property in the header row, named range, first column on the 'lister' sheet, headers, rows: label, code, URI) |
| `TYPE` | internal column outside the table (not imported): dropdown only, no codes or URIs ("tier" before 24 November 2026) |

## Functions

### `ensure_lists`

```python
def ensure_lists(wb, sheet: str='vokabular') -> list[str]
```

Write the 'lister' sheet, the named ranges and the dropdowns (data rows of the Excel table).

Values the tools recognise are written as the list label, e.g. direct-from-source -> sitat fra kilde,
basert på kjelde -> basert på kilde, Kandidat -> kandidat, public -> allmennheten, so that they match the
dropdown and the SharePoint choice columns. Other values are left as they are (the checker reports them).
Only for workbooks in the current layout (row of technical names under the properties). Returns the columns
that got a dropdown.

### `save_workbook`

```python
def save_workbook(wb, path) -> None
```

Save a workbook after restoring the value lists and dropdowns (see module docstring).

## Internal helpers

Documented in the source: `_dropdown`, `_to_label`, `_header_row`.

# `vocabtool.validate`

Source: [`vocabtool/validate.py`](../../vocabtool/validate.py)

Deterministic checks on a vocabulary read by reader.read_workbook.

Rule codes are local to this tool (prefix VT-). Where a check corresponds to a
rule in the SKOS field instructions, the instruction ID is given in `ref`.
Severity: error = must be fixed before publishing; warning = review;
info = expected gap (e.g. nn labels left for the expert) or heuristic hint.

## Constants

| Name | Meaning |
| --- | --- |
| `STATUS_VALUES` | allowed values of euvoc:status (the template's statusliste) |
| `TYPES` | allowed values of the internal column type (1, 2, 3) |
| `SOURCE_RELATIONS` | skosno:relationshipWithSource |
| `PREFIX_RE` | a vok: prefix in a table cell (v8/v9 write the concept name only) |
| `KODE_RE` | code-list references: kept until code lists are decided |
| `RULES` | rule ID -> (severity, description, reference to the instruction or source rule) |

## class `Finding`

One result of a check.

**Attributes**

- `rule`: rule ID, e.g. VT-REQ-DEF (see RULES).
- `severity`: error, warning or info.
- `key`: row key of the concept, or None for scheme-level findings.
- `sheet`: sheet name.
- `row`: row number in the sheet.
- `message`: rule text, with details after a colon.
- `ref`: reference to the instruction or source rule (e.g. S11), may be empty.

### `Finding.as_dict`: `as_dict(self)`

The finding as a dict (for the JSON report).

## Functions

### `validate`

```python
def validate(v: Vocabulary) -> list[Finding]
```

Run all VT rules on a vocabulary.

The rules and their severities are listed in RULES and in the README. Checks that need the whole vocabulary
(cycles, broader/related clashes, collections, type-1 isolation) run after the per-concept checks.

**Args**

- `v`: the vocabulary from reader.read_workbook.

**Returns**

The findings, in the order they were found.

### `summarise`

```python
def summarise(findings: list[Finding]) -> dict
```

Counts of errors, warnings and info, and one entry per rule (severity, rule, count, description).

## Internal helpers

Documented in the source: `_f`, `_find_cycles`, `_ancestors`, `_noted`, `_is_variant_pair`, `_collection_findings`.

# `vocabtool.clash_notes`

Source: [`vocabtool/clash_notes.py`](../../vocabtool/clash_notes.py)

Draft scope notes that warn about label clashes, naming the other concept by ID.

Example: "Caution: 'treble crochet' is the UK name of this concept and the US name of
HEKL-0010 (treble crochet)." The notes are drafts for expert review.

## Constants

| Name | Meaning |
| --- | --- |
| `TAG_NAMES` | language tag -> name used in the note text |

## Functions

### `clash_notes`

```python
def clash_notes(v: Vocabulary) -> dict[str, str]
```

Draft scope notes for terms that several concepts use.

**Returns**

{concept key: note text}; each note names the other concept(s) by ID, so the checker reports the clash as documented (VT-LABEL-NOTED).

## Internal helpers

Documented in the source: `_kind`, `_who`.

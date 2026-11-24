# `vocabtool.rename`

Source: [`vocabtool/rename.py`](../../vocabtool/rename.py)

Rename a concept: change its name in column B and every reference to it.

References are updated in the relation columns (broader, isPartOf, related) and in notes
(scopeNote, editorialNote, any language). Column A and endringshash are formulas and follow by themselves.
Collection sentences in scope notes ("Inngår i samlingen X.") are left alone: a collection is renamed
with rename_collection, which changes only those sentences.

## Constants

| Name | Meaning |
| --- | --- |
| `NOTE_PREFIXES` | note fields (any language) in which concept names are replaced |

## Functions

### `rename`

```python
def rename(path: str, renames: dict[str, str]) -> dict
```

Rename concepts and update every reference to them.

Changes the name in column B and the same name in relations (broader, isPartOf, related) and in scope and
editorial notes (any language). Collection sentences ("Inngår i samlingen X.") are left alone.

**Args**

- `path`: the workbook, changed in place.
- `renames`: {old name: new name}.

**Returns**

Counts: names, relations, notes.

**Raises**

- `ValueError`: an old name does not exist, a new name is not CamelCase, or it is already used.

### `rename_collection`

```python
def rename_collection(path: str, old: str, new: str) -> dict
```

Rename a collection in every main-language scope-note sentence that names it.
`old` may be the name as written or its CamelCase form; `new` is written as given.

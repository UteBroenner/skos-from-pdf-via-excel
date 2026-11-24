# `vocabtool.owl_import`

Source: [`vocabtool/owl_import.py`](../../vocabtool/owl_import.py)

Add the classes of OWL ontologies as concepts to a v9 workbook, merging with existing concepts.

Merging (an existing concept is the same as a class):
- same main-language label or alt label (normalised: case, spaces, punctuation, text in parentheses), and the
  label is used by only one class in the file; or
- a reviewed merge map (JSON: class IRI -> concept name) for spelling or wording variants, e.g. classes with the
  same code. The class label is then recorded in the editorial note.
A merged concept gets the class IRI in skos:exactMatch. Notation (from `kode`) and English label are filled only
where empty; a different notation is listed as a conflict in the log, never overwritten. A different parent class
is added as a second broader concept and flagged for the expert in the editorial note ("[fagekspert] To overbegreper: …").

New concepts (one row per class):
- label from rdfs:label@no/nb (first letter lower case unless an acronym), English label from @en; a class
  without a label gets a term from its IRI, flagged in the editorial note
- a label used by several classes, or already used in the workbook, gets the parent class as qualifier
  ("fundament, pilar"), in both languages
- notation = `kode`, broader = parent class, exactMatch = class IRI, source = ontology IRI,
  editorial note with chapter/section (`kapittel`, `avsnitt`) and "[mangler] definisjon"
- status kandidat, created today, contact point if given; type if given (e.g. 1: the classes become OWL classes)
- --derive-code-definitions: a new concept with a code and no other definition gets one built from the code table,
  e.g. "kodeverdi 59 under «buebru og hvelvbru» i V440 (kap. V-6, avsnitt V-6.1)", relationshipWithSource
  derived-from-source and "[avledet]" in the editorial note (checker: VT-DEF-DERIVED, info)
- --link <v9 workbook>: a new concept whose label matches exactly one concept with a definition there gets
  exactMatch to it, its definition copied, source = that concept and relationshipWithSource direct-from-source

Skipped: deprecated classes, and the technical root (the single top class of a file, e.g. "Rotobjekt for v440"),
unless keep_root is set. Code values (individuals) and properties are not imported.

## Functions

### `norm`

```python
def norm(s) -> str
```

Label match key: text in parentheses removed; case, spaces, hyphens, slashes and commas ignored.

### `lower_first`

```python
def lower_first(t: str | None) -> str | None
```

Lower-case first letter, unless the term starts with an acronym (G/S areal, ROS-analyse).

### `read_classes`

```python
def read_classes(path) -> tuple[str, dict]
```

(ontology IRI, {class IRI: {no, en, parents, kode, kapittel, avsnitt, deprecated}})

### `owl_import`

```python
def owl_import(workbook, owls: list, out, *, link=None, merge_map=None, contact=None, keep_root=False, kortnavn=None, title=None, derive_code_definitions=False, concept_type=None) -> dict
```

Add the classes of OWL ontologies to a workbook as concepts, merging with existing concepts.

The merge, link and flag rules are described in the module docstring.

**Args**

- `workbook`: the workbook to add to (an empty template for a new vocabulary).
- `owls`: OWL files (Turtle), imported in this order.
- `out`: the workbook to write.
- `link`: another workbook; a new concept whose label matches exactly one concept with a definition there gets exactMatch to it and its definition copied (merge rule).
- `merge_map`: {class IRI: concept name} (dict or JSON file) for reviewed merges of variant labels.
- `contact`: dcat:contactPoint for new concepts.
- `keep_root`: also import the single top class of a file.
- `kortnavn`: kortnavn for a new vocabulary.
- `title`: dct:title for a new vocabulary.
- `derive_code_definitions`: give new code entries a definition built from code and broader, marked [avledet].
- `concept_type`: type (1, 2 or 3) for new concepts; existing concepts keep theirs.

**Returns**

A log dict: merged, new, linked, derived, skipped, conflicts.

## Internal helpers

Documented in the source: `_label`.

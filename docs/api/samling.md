# `vocabtool.samling`

Source: [`vocabtool/samling.py`](../../vocabtool/samling.py)

Collections (skos:Collection) recorded in the main-language scope note.

Editors add a fixed sentence to the scope note of each member concept:

```text
    Inngår i samlingen Hoveddata.
    Inngår i samlingene Skader, Inspeksjon.
```

Collection names are written as one would say them and separated by commas
(not "og", which may be part of a name). The scope note is the only place collections
are recorded; the tools build skos:Collection and skos:member from it.

- Collection URI: <ConceptScheme URI>/samling/<CamelCase of the name>
- skos:prefLabel of the collection: the name as written (main language)
- Only the main-language scope note is read. Collections are unordered and not nested.

## Constants

| Name | Meaning |
| --- | --- |
| `SENTENCE_RE` | the collection sentence: «Inngår i samlingen X.» or «Inngår i samlingene X, Y.» |
| `MENTION_RE` | main language: looks like an attempt |
| `OTHER_LANG_RE` | collection sentences in other languages (only the main-language note is read) |

## class `Collection`

A skos:Collection built from the scope-note sentences.

**Attributes**

- `name`: CamelCase local name (URI part).
- `label`: the name as first written (skos:prefLabel of the collection).
- `members`: concept keys, in workbook order.
- `spellings`: all spellings seen (VT-COLL-SPELLING when more than one).

## Functions

### `scope_note_field`

```python
def scope_note_field(v: Vocabulary) -> str
```

The main-language scope-note field, where the collection sentence is read.

### `parse_sentence`

```python
def parse_sentence(text: str | None) -> list[tuple[str, str]]
```

[(form, name), ...] for every collection sentence in the text.

### `collection_uri`

```python
def collection_uri(scheme_uri: str, name: str) -> str
```

<ConceptScheme URI>/samling/<name>.

### `collections`

```python
def collections(v: Vocabulary) -> dict[str, Collection]
```

{CamelCase name: Collection} from the main-language scope notes.

### `sentence_problems`

```python
def sentence_problems(v: Vocabulary)
```

Yield (concept, rule, detail) for sentences the tools cannot use as written.

### `rename_in_text`

```python
def rename_in_text(text: str, old: str, new: str) -> str
```

Rename collection `old` (as written, or its CamelCase name) to `new` inside the sentences only.

### `outside_sentences`

```python
def outside_sentences(text: str, fn) -> str
```

Apply fn to the parts of the text that are not collection sentences.

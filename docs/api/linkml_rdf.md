# `vocabtool.linkml_rdf`

Source: [`vocabtool/linkml_rdf.py`](../../vocabtool/linkml_rdf.py)

Excel (v8/v9) -> LinkML data (YAML) -> RDF Turtle, plus SHACL validation.

The LinkML schema (schema/svv_vokabular.yaml) is the single source of truth.
This module adds what the standard LinkML tooling (1.12) does not do:

* RDF writer that applies per-slot ``in_language`` tags and writes enum
  ``meaning`` URIs (the stock rdflib dumper writes plain literals);
* SHACL post-processing: for slots that share one property (skos:prefLabel @nb/@en/@nn,
  dct:contributor), the generated property shapes each carry sh:maxCount 1 on the
  same path, which rejects valid data. They are replaced by qualified shapes per language.

## Constants

| Name | Meaning |
| --- | --- |
| `ROOT` | repository root |
| `SCHEMA` | the LinkML schema |
| `CROSS_ROW_SHAPES` | hand-written SHACL-SPARQL rules across rows |
| `FIELD_TO_SLOT` | reader field -> schema slot |
| `RELATION_SLOTS` | slots whose values are concept names, turned into concept URIs |
| `BASE` | base of the ConceptScheme URIs |
| `IRI_RE` | values accepted as IRIs in uri slots (http, https, urn); other values are reported, not written |

## Functions

### `schemaview`

```python
def schemaview() -> SchemaView
```

SchemaView of schema/svv_vokabular.yaml.

### `workbook_to_data`

```python
def workbook_to_data(v: Vocabulary, sv: SchemaView | None=None) -> dict
```

Build a LinkML instance (dict) of ConceptScheme from a v8/v9 workbook.

### `data_to_graph`

```python
def data_to_graph(data: dict, sv: SchemaView | None=None, skipped: list | None=None) -> Graph
```

Write RDF. Values that cannot be IRIs (for a uri/Concept range) are not written
but appended to ``skipped`` as (subject, slot, value).

### `build_shapes`

```python
def build_shapes(generated_shacl: str | Path, sv: SchemaView | None=None) -> Graph
```

Generated SHACL with language-/role-specific slots fixed, plus cross-row shapes.

### `shacl_validate`

```python
def shacl_validate(data_graph: Graph, shapes: Graph)
```

Validate a data graph with pySHACL (SHACL-SPARQL enabled, warnings allowed).

**Returns**

(conforms, results), results as dicts: severity, focus, path, value, component, message.

### `write_yaml`

```python
def write_yaml(data: dict, path: str | Path)
```

Write LinkML data as YAML (UTF-8, key order kept).

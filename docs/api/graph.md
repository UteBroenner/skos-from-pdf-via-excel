# `vocabtool.graph`

Source: [`vocabtool/graph.py`](../../vocabtool/graph.py)

Build a self-contained interactive graph page (no external JS libraries).

## Constants

| Name | Meaning |
| --- | --- |
| `TEMPLATE` | the HTML page the data is embedded in |
| `EDGE_TYPE` | relation field -> edge type on the graph page |

## Functions

### `graph_data`

```python
def graph_data(v: Vocabulary, findings: list[Finding]) -> dict
```

Nodes, edges and findings for the graph page.

**Args**

- `v`: the vocabulary.
- `findings`: findings to mark on the nodes.

**Returns**

A dict with nodes (concepts and collections, with labels, definitions, type and issues), edges (broader, isPartOf, related, member), dangling relation targets and metadata.

### `write_graph`

```python
def write_graph(v: Vocabulary, findings: list[Finding], dst: str | Path, title: str | None=None) -> Path
```

Write the self-contained graph page (vocabtool/graph_template.html with the data embedded).

**Args**

- `v`: the vocabulary.
- `findings`: findings to mark.
- `dst`: the .html file to write.
- `title`: page title; default "<kortnavn> concept graph".

**Returns**

The path written.

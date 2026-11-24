# vocabtool API reference

Generated from the docstrings by `python tools/gen_api_docs.py`; do not edit these pages by hand.
Command-line use is described in the [README](../../README.md); the command reference is in [cli](cli.md).

| Module | Purpose |
| --- | --- |
| [vocabtool](vocabtool.md) | vocabtool: tools for SKOS vocabularies kept in the Statens vegvesen Excel template (v7, v8, v9). |
| [clash_notes](clash_notes.md) | Draft scope notes that warn about label clashes, naming the other concept by ID. |
| [cli](cli.md) | Command line: python -m vocabtool <command> ... |
| [extract](extract.md) | Extraction of concepts from text (TXT converted from PDF), one LLM agent per chapter. |
| [graph](graph.md) | Build a self-contained interactive graph page (no external JS libraries). |
| [linkml_rdf](linkml_rdf.md) | Excel (v8/v9) -> LinkML data (YAML) -> RDF Turtle, plus SHACL validation. |
| [lists](lists.md) | Value lists of the template (hidden sheet 'lister') and their dropdowns in the vokabular sheet. |
| [migrate](migrate.md) | Migrate a v7 workbook into the v9 template. |
| [owl_import](owl_import.md) | Add the classes of OWL ontologies as concepts to a v9 workbook, merging with existing concepts. |
| [reader](reader.md) | Read SKOS vocabulary workbooks (template v7, v8 and v9) into plain records. |
| [rename](rename.md) | Rename a concept: change its name in column B and every reference to it. |
| [samling](samling.md) | Collections (skos:Collection) recorded in the main-language scope note. |
| [set_fields](set_fields.md) | Write reviewed values into concepts of a v9 workbook, by concept name (column B). |
| [template_ext](template_ext.md) | Template upkeep: language columns, formulas, the Excel table and header colours. |
| [uri](uri.md) | Readable concept URIs: <ConceptScheme URI>/<LocalName>. |
| [validate](validate.md) | Deterministic checks on a vocabulary read by reader.read_workbook. |

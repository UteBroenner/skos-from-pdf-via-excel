"""vocabtool: tools for SKOS vocabularies kept in the Statens vegvesen Excel template (v7, v8, v9).

Modules, in the order data flows through them:

- reader: read a workbook into Vocabulary / Concept records
- validate: the VT rules (checker)
- graph: interactive HTML graph page
- linkml_rdf: workbook -> LinkML data (YAML) -> RDF Turtle, SHACL validation
- migrate: v7 workbook -> v9 template
- template_ext, lists: template upkeep (formulas, Excel table, colours, value lists, dropdowns, language columns)
- uri, rename, samling, clash_notes: concept names, renaming, collections, label-clash notes
- owl_import, extract, set_fields: adding content (OWL classes, concepts from text, reviewed values)
- cli: the command line (python -m vocabtool <command>)
"""

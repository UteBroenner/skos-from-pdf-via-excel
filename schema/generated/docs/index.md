# SKOS-vokabular (Excel-mal v8)

Model of one vocabulary (skos:ConceptScheme) and its concepts as captured in SKOS-Excel-mal-v8. Code lists (kodeverk) are not modelled here. Each slot is annotated with its v8 Excel column (excel_column) and the technical column name in row 22 (excel_name), which is also intended as the SharePoint List internal column name. Language tags (in_language) and enum meanings are applied by the project's RDF writer (vocabtool/linkml_rdf.py); the standard LinkML RDF dumper ignores them.

URI: http://example.org/vegvesen/vokabular/def/schema

Name: svv_vokabular



## Classes

| Class | Description |
| --- | --- |
| [Collection](Collection.md) | A group of concepts, recorded in the main-language scope note of each member ... |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |
| [ConceptScheme](ConceptScheme.md) | One vocabulary = one Excel workbook (vokabular sheet, rows 1-16) |



## Slots

| Slot | Description |
| --- | --- |
| [alt_label_de](alt_label_de.md) |  |
| [alt_label_en](alt_label_en.md) |  |
| [alt_label_en_gb](alt_label_en_gb.md) |  |
| [alt_label_en_us](alt_label_en_us.md) |  |
| [alt_label_es](alt_label_es.md) |  |
| [alt_label_nb](alt_label_nb.md) |  |
| [alt_label_nn](alt_label_nn.md) |  |
| [audience](audience.md) |  |
| [broader](broader.md) |  |
| [close_match](close_match.md) |  |
| [collections](collections.md) | Container slot for the data file only |
| [concepts](concepts.md) | Container slot for the data file only |
| [contact_point](contact_point.md) | E-mail address or web address |
| [created](created.md) |  |
| [created_by](created_by.md) | Hidden column; template formula = dct:creator of the vocabulary (cell B16) |
| [creator](creator.md) |  |
| [data_structure_label](data_structure_label.md) |  |
| [definition_en](definition_en.md) |  |
| [definition_en_us](definition_en_us.md) |  |
| [definition_nb](definition_nb.md) | Required when the main language is nb (SHACL rule) |
| [definition_nn](definition_nn.md) |  |
| [editorial_note](editorial_note.md) |  |
| [end_date](end_date.md) |  |
| [exact_match](exact_match.md) |  |
| [example](example.md) |  |
| [hidden_label](hidden_label.md) | Discouraged term, e |
| [identifier](identifier.md) | <kortnavn>-<concept name>, e |
| [in_scheme](in_scheme.md) | Set by the converter from the scheme URI |
| [is_part_of](is_part_of.md) |  |
| [issued](issued.md) | System-generated at publication |
| [kortnavn](kortnavn.md) | Short name of the vocabulary, letters, digits and hyphens, e |
| [main_language](main_language.md) | BCP 47 tag of the language in which every concept must have a prefLabel and a... |
| [member](member.md) | Concepts whose main-language scope note names the collection |
| [modified](modified.md) |  |
| [modified_by](modified_by.md) |  |
| [notation](notation.md) |  |
| [pref_label_de](pref_label_de.md) |  |
| [pref_label_en](pref_label_en.md) |  |
| [pref_label_en_gb](pref_label_en_gb.md) |  |
| [pref_label_en_us](pref_label_en_us.md) |  |
| [pref_label_es](pref_label_es.md) |  |
| [pref_label_nb](pref_label_nb.md) | Recommended term, bokmål |
| [pref_label_nn](pref_label_nn.md) | Obligatory in the template, but left empty by extraction for the expert (S06) |
| [publisher](publisher.md) | System-generated at publication |
| [related](related.md) |  |
| [relation_role](relation_role.md) |  |
| [relationship_with_source](relationship_with_source.md) |  |
| [scope_note](scope_note.md) |  |
| [scope_note_en_us](scope_note_en_us.md) | Usage note in US English, e |
| [source](source.md) |  |
| [start_date](start_date.md) |  |
| [status](status.md) |  |
| [subject](subject.md) | Subject area |
| [tier](tier.md) | 1 = physical objects, spatial concepts, measurable properties; 2 = processes ... |
| [title](title.md) |  |
| [uri](uri.md) | Concept or scheme URI |
| [value_range](value_range.md) |  |
| [version_info](version_info.md) |  |
| [version_notes](version_notes.md) |  |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [ConceptStatus](ConceptStatus.md) | Status values from the template's statusliste, mapped to the EU concept-statu... |


## Types

| Type | Description |
| --- | --- |
| [Boolean](Boolean.md) | A binary (true or false) value |
| [Curie](Curie.md) | a compact URI |
| [Date](Date.md) | a date (year, month and day) in an idealized calendar |
| [DateOrDatetime](DateOrDatetime.md) | Either a date or a datetime |
| [Datetime](Datetime.md) | The combination of a date and time |
| [Decimal](Decimal.md) | A real number with arbitrary precision that conforms to the xsd:decimal speci... |
| [Double](Double.md) | A real number that conforms to the xsd:double specification |
| [Float](Float.md) | A real number that conforms to the xsd:float specification |
| [Integer](Integer.md) | An integer |
| [Jsonpath](Jsonpath.md) | A string encoding a JSON Path |
| [Jsonpointer](Jsonpointer.md) | A string encoding a JSON Pointer |
| [Ncname](Ncname.md) | Prefix part of CURIE |
| [Nodeidentifier](Nodeidentifier.md) | A URI, CURIE or BNODE that represents a node in a model |
| [Objectidentifier](Objectidentifier.md) | A URI or CURIE that represents an object in the model |
| [Sparqlpath](Sparqlpath.md) | A string encoding a SPARQL Property Path |
| [String](String.md) | A character string |
| [Time](Time.md) | A time object represents a (local) time of day, independent of any particular... |
| [Uri](Uri.md) | a complete URI |
| [Uriorcurie](Uriorcurie.md) | a URI or a CURIE |


## Subsets

| Subset | Description |
| --- | --- |

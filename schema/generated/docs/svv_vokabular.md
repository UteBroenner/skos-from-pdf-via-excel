# svv_vokabular 

Model of one vocabulary (skos:ConceptScheme) and its concepts as captured in SKOS-Excel-mal-v8. Code lists (kodeverk) are not modelled here. Each slot is annotated with its v8 Excel column (excel_column) and the technical column name in row 22 (excel_name), which is also intended as the SharePoint List internal column name. Language tags (in_language) and enum meanings are applied by the project's RDF writer (vocabtool/linkml_rdf.py); the standard LinkML RDF dumper ignores them.

URI: http://example.org/vegvesen/vokabular/def/schema
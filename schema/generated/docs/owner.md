---
search:
  boost: 5.0
---

# Slot: owner 


_Begrepseier: a prov:Person, written as the name (foaf:name). Intended RDF form: prov:qualifiedAttribution [ prov:agent <person> ; prov:hadRole begrepseier ]. Persons are not converted to RDF (decision 23 November 2026); only dcat:contactPoint is kept._



<div data-search-exclude markdown="1">



URI: [prov:qualifiedAttribution](http://www.w3.org/ns/prov#qualifiedAttribution)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Concept](Concept.md) |
| Slot URI | [prov:qualifiedAttribution](http://www.w3.org/ns/prov#qualifiedAttribution) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AB |
| excel_name | begrepseier |
| rdf | skipped |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | prov:qualifiedAttribution |
| native | svv:owner |




## LinkML Source

<details>
```yaml
name: owner
annotations:
  excel_column:
    tag: excel_column
    value: AB
  excel_name:
    tag: excel_name
    value: begrepseier
  rdf:
    tag: rdf
    value: skipped
description: 'Begrepseier: a prov:Person, written as the name (foaf:name). Intended
  RDF form: prov:qualifiedAttribution [ prov:agent <person> ; prov:hadRole begrepseier
  ]. Persons are not converted to RDF (decision 23 November 2026); only dcat:contactPoint
  is kept.'
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: prov:qualifiedAttribution
domain_of:
- Concept
range: string

```
</details></div>
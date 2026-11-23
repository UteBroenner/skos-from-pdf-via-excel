---
search:
  boost: 5.0
---

# Slot: created_by 


_Opprettet av: a prov:Person, written as the name (foaf:name); hidden column, template formula = dct:creator of the vocabulary (cell B16). Persons are not converted to RDF; only dcat:contactPoint is kept._



<div data-search-exclude markdown="1">



URI: [dct:creator](http://purl.org/dc/terms/creator)
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
| Slot URI | [dct:creator](http://purl.org/dc/terms/creator) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AD |
| excel_name | opprettet_av |
| hidden | True |
| rdf | skipped |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:creator |
| native | svv:created_by |




## LinkML Source

<details>
```yaml
name: created_by
annotations:
  excel_column:
    tag: excel_column
    value: AD
  excel_name:
    tag: excel_name
    value: opprettet_av
  hidden:
    tag: hidden
    value: true
  rdf:
    tag: rdf
    value: skipped
description: 'Opprettet av: a prov:Person, written as the name (foaf:name); hidden
  column, template formula = dct:creator of the vocabulary (cell B16). Persons are
  not converted to RDF; only dcat:contactPoint is kept.'
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dct:creator
domain_of:
- Concept
range: string

```
</details></div>
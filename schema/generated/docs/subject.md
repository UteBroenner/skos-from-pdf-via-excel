---
search:
  boost: 5.0
---

# Slot: subject 


_Subject area. Template allows rdf:langString or skos:Concept; modelled as text for now._



<div data-search-exclude markdown="1">



URI: [dct:subject](http://purl.org/dc/terms/subject)
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
| Slot URI | [dct:subject](http://purl.org/dc/terms/subject) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | S |
| excel_name | fagområde |
| requirement | anbefalt |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:subject |
| native | svv:subject |




## LinkML Source

<details>
```yaml
name: subject
annotations:
  excel_column:
    tag: excel_column
    value: S
  excel_name:
    tag: excel_name
    value: fagområde
  requirement:
    tag: requirement
    value: anbefalt
description: Subject area. Template allows rdf:langString or skos:Concept; modelled
  as text for now.
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: nb
rank: 1000
slot_uri: dct:subject
domain_of:
- Concept
range: string

```
</details></div>
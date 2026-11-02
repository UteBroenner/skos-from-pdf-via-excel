---
search:
  boost: 5.0
---

# Slot: modified 

<div data-search-exclude markdown="1">



URI: [dct:modified](http://purl.org/dc/terms/modified)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Date](Date.md) |
| Domain Of | [Concept](Concept.md) |
| Slot URI | [dct:modified](http://purl.org/dc/terms/modified) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AE |
| excel_name | dato_sist_endret |
| requirement | anbefalt |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:modified |
| native | svv:modified |




## LinkML Source

<details>
```yaml
name: modified
annotations:
  excel_column:
    tag: excel_column
    value: AE
  excel_name:
    tag: excel_name
    value: dato_sist_endret
  requirement:
    tag: requirement
    value: anbefalt
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dct:modified
domain_of:
- Concept
range: date

```
</details></div>
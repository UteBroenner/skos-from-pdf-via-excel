---
search:
  boost: 5.0
---

# Slot: created 

<div data-search-exclude markdown="1">



URI: [dct:created](http://purl.org/dc/terms/created)
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
| Slot URI | [dct:created](http://purl.org/dc/terms/created) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AC |
| excel_name | dato_opprettet |
| requirement | anbefalt |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:created |
| native | svv:created |




## LinkML Source

<details>
```yaml
name: created
annotations:
  excel_column:
    tag: excel_column
    value: AC
  excel_name:
    tag: excel_name
    value: dato_opprettet
  requirement:
    tag: requirement
    value: anbefalt
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dct:created
domain_of:
- Concept
range: date

```
</details></div>
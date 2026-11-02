---
search:
  boost: 5.0
---

# Slot: relation_role 

<div data-search-exclude markdown="1">



URI: [skosno:relationRole](https://data.norge.no/vocabulary/skosno#relationRole)
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
| Slot URI | [skosno:relationRole](https://data.norge.no/vocabulary/skosno#relationRole) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | X |
| excel_name | relasjonsrolle |
| requirement | anbefalt |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skosno:relationRole |
| native | svv:relation_role |




## LinkML Source

<details>
```yaml
name: relation_role
annotations:
  excel_column:
    tag: excel_column
    value: X
  excel_name:
    tag: excel_name
    value: relasjonsrolle
  requirement:
    tag: requirement
    value: anbefalt
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: nb
rank: 1000
slot_uri: skosno:relationRole
domain_of:
- Concept
range: string

```
</details></div>
---
search:
  boost: 5.0
---

# Slot: identifier 


_<kortnavn>-<concept name>, e.g. N101-Rekkverk (formula in column A). Relations in Excel use the concept name._



<div data-search-exclude markdown="1">



URI: [dct:identifier](http://purl.org/dc/terms/identifier)
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
| Slot URI | [dct:identifier](http://purl.org/dc/terms/identifier) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |


### Value Constraints

| Property | Value |
| --- | --- |
| Regex Pattern | `^[A-Za-z0-9][A-Za-z0-9-]*$` |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | A |
| excel_name | intern_identifikator |
| requirement | obligatorisk |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:identifier |
| native | svv:identifier |




## LinkML Source

<details>
```yaml
name: identifier
annotations:
  excel_column:
    tag: excel_column
    value: A
  excel_name:
    tag: excel_name
    value: intern_identifikator
  requirement:
    tag: requirement
    value: obligatorisk
description: <kortnavn>-<concept name>, e.g. N101-Rekkverk (formula in column A).
  Relations in Excel use the concept name.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dct:identifier
domain_of:
- Concept
range: string
required: true
pattern: ^[A-Za-z0-9][A-Za-z0-9-]*$

```
</details></div>
---
search:
  boost: 5.0
---

# Slot: title 

<div data-search-exclude markdown="1">



URI: [dct:title](http://purl.org/dc/terms/title)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ConceptScheme](ConceptScheme.md) | One vocabulary = one Excel workbook (vokabular sheet, rows 1-16) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ConceptScheme](ConceptScheme.md) |
| Slot URI | [dct:title](http://purl.org/dc/terms/title) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_cell | B13 |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:title |
| native | svv:title |




## LinkML Source

<details>
```yaml
name: title
annotations:
  excel_cell:
    tag: excel_cell
    value: B13
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: nb
rank: 1000
slot_uri: dct:title
domain_of:
- ConceptScheme
range: string
required: true

```
</details></div>
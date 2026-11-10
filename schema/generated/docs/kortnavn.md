---
search:
  boost: 5.0
---

# Slot: kortnavn 


_Short name of the vocabulary, letters, digits and hyphens, e.g. N101 or crochet-us (cell B14)._



<div data-search-exclude markdown="1">



URI: [svv:kortnavn](http://example.org/vegvesen/vokabular/def#kortnavn)
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
| Slot URI | [svv:kortnavn](http://example.org/vegvesen/vokabular/def#kortnavn) |
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
| excel_cell | B14 |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | svv:kortnavn |
| native | svv:kortnavn |




## LinkML Source

<details>
```yaml
name: kortnavn
annotations:
  excel_cell:
    tag: excel_cell
    value: B14
description: Short name of the vocabulary, letters, digits and hyphens, e.g. N101
  or crochet-us (cell B14).
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: svv:kortnavn
domain_of:
- ConceptScheme
range: string
required: true
pattern: ^[A-Za-z0-9][A-Za-z0-9-]*$

```
</details></div>
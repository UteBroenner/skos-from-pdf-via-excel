---
search:
  boost: 5.0
---

# Slot: creator 

<div data-search-exclude markdown="1">



URI: [dct:creator](http://purl.org/dc/terms/creator)
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
| Slot URI | [dct:creator](http://purl.org/dc/terms/creator) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_cell | B16 |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:creator |
| native | svv:creator |




## LinkML Source

<details>
```yaml
name: creator
annotations:
  excel_cell:
    tag: excel_cell
    value: B16
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dct:creator
domain_of:
- ConceptScheme
range: string

```
</details></div>
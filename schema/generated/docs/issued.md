---
search:
  boost: 5.0
---

# Slot: issued 


_System-generated at publication._



<div data-search-exclude markdown="1">



URI: [dct:issued](http://purl.org/dc/terms/issued)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ConceptScheme](ConceptScheme.md) | One vocabulary = one Excel workbook (vokabular sheet, rows 1-16) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Date](Date.md) |
| Domain Of | [ConceptScheme](ConceptScheme.md) |
| Slot URI | [dct:issued](http://purl.org/dc/terms/issued) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_cell | B18 |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:issued |
| native | svv:issued |




## LinkML Source

<details>
```yaml
name: issued
annotations:
  excel_cell:
    tag: excel_cell
    value: B18
description: System-generated at publication.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dct:issued
domain_of:
- ConceptScheme
range: date

```
</details></div>
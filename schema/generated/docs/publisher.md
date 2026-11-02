---
search:
  boost: 5.0
---

# Slot: publisher 


_System-generated at publication._



<div data-search-exclude markdown="1">



URI: [dct:publisher](http://purl.org/dc/terms/publisher)
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
| Slot URI | [dct:publisher](http://purl.org/dc/terms/publisher) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_cell | B15 |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:publisher |
| native | svv:publisher |




## LinkML Source

<details>
```yaml
name: publisher
annotations:
  excel_cell:
    tag: excel_cell
    value: B15
description: System-generated at publication.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dct:publisher
domain_of:
- ConceptScheme
range: string

```
</details></div>
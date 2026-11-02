---
search:
  boost: 5.0
---

# Slot: modified_by 

<div data-search-exclude markdown="1">



URI: [dct:contributor](http://purl.org/dc/terms/contributor)
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
| Slot URI | [dct:contributor](http://purl.org/dc/terms/contributor) |
### Value Constraints

| Property | Value |
| --- | --- |
| Regex Pattern | `^[^@\s]+@vegvesen\.no$` |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AF |
| excel_name | sist_endret_av |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:contributor |
| native | svv:modified_by |




## LinkML Source

<details>
```yaml
name: modified_by
annotations:
  excel_column:
    tag: excel_column
    value: AF
  excel_name:
    tag: excel_name
    value: sist_endret_av
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dct:contributor
domain_of:
- Concept
range: string
pattern: ^[^@\s]+@vegvesen\.no$

```
</details></div>
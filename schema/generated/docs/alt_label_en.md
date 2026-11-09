---
search:
  boost: 5.0
---

# Slot: alt_label_en 

<div data-search-exclude markdown="1">



URI: [skos:altLabel](http://www.w3.org/2004/02/skos/core#altLabel)
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
| Slot URI | [skos:altLabel](http://www.w3.org/2004/02/skos/core#altLabel) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | L |
| excel_name | tillat_term_engelsk |
| requirement | anbefalt |
| separator | , |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:altLabel |
| native | svv:alt_label_en |




## LinkML Source

<details>
```yaml
name: alt_label_en
annotations:
  excel_column:
    tag: excel_column
    value: L
  excel_name:
    tag: excel_name
    value: tillat_term_engelsk
  requirement:
    tag: requirement
    value: anbefalt
  separator:
    tag: separator
    value: ','
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: en
rank: 1000
slot_uri: skos:altLabel
domain_of:
- Concept
range: string
multivalued: true

```
</details></div>
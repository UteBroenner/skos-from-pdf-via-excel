---
search:
  boost: 5.0
---

# Slot: pref_label_en 

<div data-search-exclude markdown="1">



URI: [skos:prefLabel](http://www.w3.org/2004/02/skos/core#prefLabel)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |
| [Collection](Collection.md) | A group of concepts, recorded in the main-language scope note of each member ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Concept](Concept.md), [Collection](Collection.md) |
| Slot URI | [skos:prefLabel](http://www.w3.org/2004/02/skos/core#prefLabel) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | D |
| excel_name | anbefalt_term_engelsk |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:prefLabel |
| native | svv:pref_label_en |




## LinkML Source

<details>
```yaml
name: pref_label_en
annotations:
  excel_column:
    tag: excel_column
    value: D
  excel_name:
    tag: excel_name
    value: anbefalt_term_engelsk
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: en
rank: 1000
slot_uri: skos:prefLabel
domain_of:
- Concept
- Collection
range: string

```
</details></div>
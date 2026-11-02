---
search:
  boost: 5.0
---

# Slot: pref_label_nn 


_Obligatory in the template, but left empty by extraction for the expert (S06)._



<div data-search-exclude markdown="1">



URI: [skos:prefLabel](http://www.w3.org/2004/02/skos/core#prefLabel)
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
| Slot URI | [skos:prefLabel](http://www.w3.org/2004/02/skos/core#prefLabel) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | E |
| excel_name | anbefalt_term_nynorsk |
| requirement | obligatorisk |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:prefLabel |
| native | svv:pref_label_nn |




## LinkML Source

<details>
```yaml
name: pref_label_nn
annotations:
  excel_column:
    tag: excel_column
    value: E
  excel_name:
    tag: excel_name
    value: anbefalt_term_nynorsk
  requirement:
    tag: requirement
    value: obligatorisk
description: Obligatory in the template, but left empty by extraction for the expert
  (S06).
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: nn
rank: 1000
slot_uri: skos:prefLabel
domain_of:
- Concept
range: string

```
</details></div>
---
search:
  boost: 5.0
---

# Slot: pref_label_en_gb 

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
| excel_column | AQ |
| excel_name | anbefalt_term_engelsk_gb |
| requirement | valgfri |
| template | v8-lang-ext |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:prefLabel |
| native | svv:pref_label_en_gb |




## LinkML Source

<details>
```yaml
name: pref_label_en_gb
annotations:
  excel_column:
    tag: excel_column
    value: AQ
  excel_name:
    tag: excel_name
    value: anbefalt_term_engelsk_gb
  requirement:
    tag: requirement
    value: valgfri
  template:
    tag: template
    value: v8-lang-ext
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: en-GB
rank: 1000
slot_uri: skos:prefLabel
domain_of:
- Concept
range: string

```
</details></div>
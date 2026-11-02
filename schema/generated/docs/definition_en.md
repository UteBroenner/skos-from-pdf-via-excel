---
search:
  boost: 5.0
---

# Slot: definition_en 

<div data-search-exclude markdown="1">



URI: [skos:definition](http://www.w3.org/2004/02/skos/core#definition)
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
| Slot URI | [skos:definition](http://www.w3.org/2004/02/skos/core#definition) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | H |
| excel_name | definisjon_engelsk |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:definition |
| native | svv:definition_en |




## LinkML Source

<details>
```yaml
name: definition_en
annotations:
  excel_column:
    tag: excel_column
    value: H
  excel_name:
    tag: excel_name
    value: definisjon_engelsk
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: en
rank: 1000
slot_uri: skos:definition
domain_of:
- Concept
range: string

```
</details></div>
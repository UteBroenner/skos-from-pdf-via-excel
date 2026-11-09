---
search:
  boost: 5.0
---

# Slot: definition_en_us 

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
| excel_column | AV |
| excel_name | definisjon_engelsk_us |
| requirement | valgfri |
| template | v8-lang-ext |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:definition |
| native | svv:definition_en_us |




## LinkML Source

<details>
```yaml
name: definition_en_us
annotations:
  excel_column:
    tag: excel_column
    value: AV
  excel_name:
    tag: excel_name
    value: definisjon_engelsk_us
  requirement:
    tag: requirement
    value: valgfri
  template:
    tag: template
    value: v8-lang-ext
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: en-US
rank: 1000
slot_uri: skos:definition
domain_of:
- Concept
range: string

```
</details></div>
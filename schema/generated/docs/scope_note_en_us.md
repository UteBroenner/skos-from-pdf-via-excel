---
search:
  boost: 5.0
---

# Slot: scope_note_en_us 


_Usage note in US English, e.g. a warning that a term means another concept elsewhere._



<div data-search-exclude markdown="1">



URI: [skos:scopeNote](http://www.w3.org/2004/02/skos/core#scopeNote)
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
| Slot URI | [skos:scopeNote](http://www.w3.org/2004/02/skos/core#scopeNote) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AY |
| excel_name | merknad_engelsk_us |
| requirement | valgfri |
| template | v8-lang-ext |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:scopeNote |
| native | svv:scope_note_en_us |




## LinkML Source

<details>
```yaml
name: scope_note_en_us
annotations:
  excel_column:
    tag: excel_column
    value: AY
  excel_name:
    tag: excel_name
    value: merknad_engelsk_us
  requirement:
    tag: requirement
    value: valgfri
  template:
    tag: template
    value: v8-lang-ext
description: Usage note in US English, e.g. a warning that a term means another concept
  elsewhere.
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: en-US
rank: 1000
slot_uri: skos:scopeNote
domain_of:
- Concept
range: string

```
</details></div>
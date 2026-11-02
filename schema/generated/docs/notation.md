---
search:
  boost: 5.0
---

# Slot: notation 

<div data-search-exclude markdown="1">



URI: [skos:notation](http://www.w3.org/2004/02/skos/core#notation)
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
| Slot URI | [skos:notation](http://www.w3.org/2004/02/skos/core#notation) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | F |
| excel_name | notasjon_eller_kode |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:notation |
| native | svv:notation |




## LinkML Source

<details>
```yaml
name: notation
annotations:
  excel_column:
    tag: excel_column
    value: F
  excel_name:
    tag: excel_name
    value: notasjon_eller_kode
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: skos:notation
domain_of:
- Concept
range: string

```
</details></div>
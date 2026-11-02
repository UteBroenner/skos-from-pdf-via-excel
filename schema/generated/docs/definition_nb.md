---
search:
  boost: 5.0
---

# Slot: definition_nb 

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
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | G |
| excel_name | definisjon_bokmål |
| requirement | obligatorisk |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:definition |
| native | svv:definition_nb |




## LinkML Source

<details>
```yaml
name: definition_nb
annotations:
  excel_column:
    tag: excel_column
    value: G
  excel_name:
    tag: excel_name
    value: definisjon_bokmål
  requirement:
    tag: requirement
    value: obligatorisk
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: nb
rank: 1000
slot_uri: skos:definition
domain_of:
- Concept
range: string
required: true

```
</details></div>
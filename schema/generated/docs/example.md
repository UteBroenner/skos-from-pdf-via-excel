---
search:
  boost: 5.0
---

# Slot: example 

<div data-search-exclude markdown="1">



URI: [skos:example](http://www.w3.org/2004/02/skos/core#example)
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
| Slot URI | [skos:example](http://www.w3.org/2004/02/skos/core#example) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | R |
| excel_name | eksempel |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:example |
| native | svv:example |




## LinkML Source

<details>
```yaml
name: example
annotations:
  excel_column:
    tag: excel_column
    value: R
  excel_name:
    tag: excel_name
    value: eksempel
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: skos:example
domain_of:
- Concept
range: string

```
</details></div>
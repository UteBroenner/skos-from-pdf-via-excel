---
search:
  boost: 5.0
---

# Slot: broader 

<div data-search-exclude markdown="1">



URI: [skos:broader](http://www.w3.org/2004/02/skos/core#broader)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Concept](Concept.md) |
| Domain Of | [Concept](Concept.md) |
| Slot URI | [skos:broader](http://www.w3.org/2004/02/skos/core#broader) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | U |
| excel_name | har_overbegrep |
| requirement | valgfri |
| excel_value | concept name (column B) |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:broader |
| native | svv:broader |




## LinkML Source

<details>
```yaml
name: broader
annotations:
  excel_column:
    tag: excel_column
    value: U
  excel_name:
    tag: excel_name
    value: har_overbegrep
  requirement:
    tag: requirement
    value: valgfri
  excel_value:
    tag: excel_value
    value: concept name (column B)
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: skos:broader
domain_of:
- Concept
range: Concept
multivalued: true

```
</details></div>
---
search:
  boost: 5.0
---

# Slot: value_range 

<div data-search-exclude markdown="1">



URI: [skosno:valueRange](https://data.norge.no/vocabulary/skosno#valueRange)
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
| Slot URI | [skosno:valueRange](https://data.norge.no/vocabulary/skosno#valueRange) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AM |
| excel_name | verdiområde |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skosno:valueRange |
| native | svv:value_range |




## LinkML Source

<details>
```yaml
name: value_range
annotations:
  excel_column:
    tag: excel_column
    value: AM
  excel_name:
    tag: excel_name
    value: verdiområde
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: skosno:valueRange
domain_of:
- Concept
range: string

```
</details></div>
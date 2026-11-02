---
search:
  boost: 5.0
---

# Slot: contact_point 

<div data-search-exclude markdown="1">



URI: [dcat:contactPoint](http://www.w3.org/ns/dcat#contactPoint)
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
| Slot URI | [dcat:contactPoint](http://www.w3.org/ns/dcat#contactPoint) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |


### Value Constraints

| Property | Value |
| --- | --- |
| Regex Pattern | `^[^@\s]+@vegvesen\.no$` |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AA |
| excel_name | kontaktpunkt |
| requirement | obligatorisk |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dcat:contactPoint |
| native | svv:contact_point |




## LinkML Source

<details>
```yaml
name: contact_point
annotations:
  excel_column:
    tag: excel_column
    value: AA
  excel_name:
    tag: excel_name
    value: kontaktpunkt
  requirement:
    tag: requirement
    value: obligatorisk
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dcat:contactPoint
domain_of:
- Concept
range: string
required: true
pattern: ^[^@\s]+@vegvesen\.no$

```
</details></div>
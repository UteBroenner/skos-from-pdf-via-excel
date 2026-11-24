---
search:
  boost: 5.0
---

# Slot: type 


_1 = physical objects, spatial concepts, measurable properties; 2 = processes and states; 3 = normative requirements. Only type 1 becomes OWL classes. Called tier before 24 November 2026._



<div data-search-exclude markdown="1">



URI: [svv:type](http://example.org/vegvesen/vokabular/def#type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [Concept](Concept.md) |
| Slot URI | [svv:type](http://example.org/vegvesen/vokabular/def#type) |
### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 1 |
| Maximum Value | 3 |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AO (base template), AY (language extension): always the last column, outside the Excel table |
| excel_name | type |
| requirement | internt |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | svv:type |
| native | svv:type |




## LinkML Source

<details>
```yaml
name: type
annotations:
  excel_column:
    tag: excel_column
    value: 'AO (base template), AY (language extension): always the last column, outside
      the Excel table'
  excel_name:
    tag: excel_name
    value: type
  requirement:
    tag: requirement
    value: internt
description: 1 = physical objects, spatial concepts, measurable properties; 2 = processes
  and states; 3 = normative requirements. Only type 1 becomes OWL classes. Called
  tier before 24 November 2026.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: svv:type
domain_of:
- Concept
range: integer
minimum_value: 1
maximum_value: 3

```
</details></div>
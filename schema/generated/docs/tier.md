---
search:
  boost: 5.0
---

# Slot: tier 


_1 = physical objects, spatial concepts, measurable properties; 2 = processes and states; 3 = normative requirements. Only Tier 1 becomes OWL classes._



<div data-search-exclude markdown="1">



URI: [svv:tier](http://example.org/vegvesen/vokabular/def#tier)
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
| Slot URI | [svv:tier](http://example.org/vegvesen/vokabular/def#tier) |
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
| excel_name | tier |
| requirement | internt |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | svv:tier |
| native | svv:tier |




## LinkML Source

<details>
```yaml
name: tier
annotations:
  excel_column:
    tag: excel_column
    value: 'AO (base template), AY (language extension): always the last column, outside
      the Excel table'
  excel_name:
    tag: excel_name
    value: tier
  requirement:
    tag: requirement
    value: internt
description: 1 = physical objects, spatial concepts, measurable properties; 2 = processes
  and states; 3 = normative requirements. Only Tier 1 becomes OWL classes.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: svv:tier
domain_of:
- Concept
range: integer
minimum_value: 1
maximum_value: 3

```
</details></div>
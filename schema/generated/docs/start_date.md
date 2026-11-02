---
search:
  boost: 5.0
---

# Slot: start_date 

<div data-search-exclude markdown="1">



URI: [euvoc:startDate](http://publications.europa.eu/ontology/euvoc#startDate)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Date](Date.md) |
| Domain Of | [Concept](Concept.md) |
| Slot URI | [euvoc:startDate](http://publications.europa.eu/ontology/euvoc#startDate) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AJ |
| excel_name | gjelder_fra_og_med |
| requirement | anbefalt |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | euvoc:startDate |
| native | svv:start_date |




## LinkML Source

<details>
```yaml
name: start_date
annotations:
  excel_column:
    tag: excel_column
    value: AJ
  excel_name:
    tag: excel_name
    value: gjelder_fra_og_med
  requirement:
    tag: requirement
    value: anbefalt
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: euvoc:startDate
domain_of:
- Concept
range: date

```
</details></div>
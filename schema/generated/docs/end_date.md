---
search:
  boost: 5.0
---

# Slot: end_date 

<div data-search-exclude markdown="1">



URI: [euvoc:endDate](http://publications.europa.eu/ontology/euvoc#endDate)
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
| Slot URI | [euvoc:endDate](http://publications.europa.eu/ontology/euvoc#endDate) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AK |
| excel_name | gjelder_til_og_med |
| requirement | anbefalt |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | euvoc:endDate |
| native | svv:end_date |




## LinkML Source

<details>
```yaml
name: end_date
annotations:
  excel_column:
    tag: excel_column
    value: AK
  excel_name:
    tag: excel_name
    value: gjelder_til_og_med
  requirement:
    tag: requirement
    value: anbefalt
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: euvoc:endDate
domain_of:
- Concept
range: date

```
</details></div>
---
search:
  boost: 5.0
---

# Slot: status 

<div data-search-exclude markdown="1">



URI: [euvoc:status](http://publications.europa.eu/ontology/euvoc#status)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ConceptStatus](ConceptStatus.md) |
| Domain Of | [Concept](Concept.md) |
| Slot URI | [euvoc:status](http://publications.europa.eu/ontology/euvoc#status) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AI |
| excel_name | status |
| requirement | anbefalt |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | euvoc:status |
| native | svv:status |




## LinkML Source

<details>
```yaml
name: status
annotations:
  excel_column:
    tag: excel_column
    value: AI
  excel_name:
    tag: excel_name
    value: status
  requirement:
    tag: requirement
    value: anbefalt
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: euvoc:status
domain_of:
- Concept
range: ConceptStatus

```
</details></div>
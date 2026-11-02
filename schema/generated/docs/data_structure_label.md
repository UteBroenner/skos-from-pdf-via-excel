---
search:
  boost: 5.0
---

# Slot: data_structure_label 

<div data-search-exclude markdown="1">



URI: [skosno:dataStructureLabel](https://data.norge.no/vocabulary/skosno#dataStructureLabel)
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
| Slot URI | [skosno:dataStructureLabel](https://data.norge.no/vocabulary/skosno#dataStructureLabel) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AL |
| excel_name | datastrukturterm |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skosno:dataStructureLabel |
| native | svv:data_structure_label |




## LinkML Source

<details>
```yaml
name: data_structure_label
annotations:
  excel_column:
    tag: excel_column
    value: AL
  excel_name:
    tag: excel_name
    value: datastrukturterm
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: skosno:dataStructureLabel
domain_of:
- Concept
range: string

```
</details></div>
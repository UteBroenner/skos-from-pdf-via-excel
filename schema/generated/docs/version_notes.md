---
search:
  boost: 5.0
---

# Slot: version_notes 

<div data-search-exclude markdown="1">



URI: [adms:versionNotes](http://www.w3.org/ns/adms#versionNotes)
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
| Slot URI | [adms:versionNotes](http://www.w3.org/ns/adms#versionNotes) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AH |
| excel_name | versjonsnote |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | adms:versionNotes |
| native | svv:version_notes |




## LinkML Source

<details>
```yaml
name: version_notes
annotations:
  excel_column:
    tag: excel_column
    value: AH
  excel_name:
    tag: excel_name
    value: versjonsnote
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: adms:versionNotes
domain_of:
- Concept
range: string

```
</details></div>
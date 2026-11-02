---
search:
  boost: 5.0
---

# Slot: version_info 

<div data-search-exclude markdown="1">



URI: [owl:versionInfo](http://www.w3.org/2002/07/owl#versionInfo)
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
| Slot URI | [owl:versionInfo](http://www.w3.org/2002/07/owl#versionInfo) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | AG |
| excel_name | versjonsnummer |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | owl:versionInfo |
| native | svv:version_info |




## LinkML Source

<details>
```yaml
name: version_info
annotations:
  excel_column:
    tag: excel_column
    value: AG
  excel_name:
    tag: excel_name
    value: versjonsnummer
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: owl:versionInfo
domain_of:
- Concept
range: string

```
</details></div>
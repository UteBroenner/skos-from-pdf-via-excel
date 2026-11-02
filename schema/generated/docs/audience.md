---
search:
  boost: 5.0
---

# Slot: audience 

<div data-search-exclude markdown="1">



URI: [dct:audience](http://purl.org/dc/terms/audience)
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
| Slot URI | [dct:audience](http://purl.org/dc/terms/audience) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | M |
| excel_name | målgruppe |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:audience |
| native | svv:audience |




## LinkML Source

<details>
```yaml
name: audience
annotations:
  excel_column:
    tag: excel_column
    value: M
  excel_name:
    tag: excel_name
    value: målgruppe
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dct:audience
domain_of:
- Concept
range: string

```
</details></div>
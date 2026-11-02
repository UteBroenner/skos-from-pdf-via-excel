---
search:
  boost: 5.0
---

# Slot: source 

<div data-search-exclude markdown="1">



URI: [dct:source](http://purl.org/dc/terms/source)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [uri](uri.md) |
| Domain Of | [Concept](Concept.md) |
| Slot URI | [dct:source](http://purl.org/dc/terms/source) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | N |
| excel_name | kilde |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dct:source |
| native | svv:source |




## LinkML Source

<details>
```yaml
name: source
annotations:
  excel_column:
    tag: excel_column
    value: N
  excel_name:
    tag: excel_name
    value: kilde
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: dct:source
domain_of:
- Concept
range: uri

```
</details></div>
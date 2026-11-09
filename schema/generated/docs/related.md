---
search:
  boost: 5.0
---

# Slot: related 

<div data-search-exclude markdown="1">



URI: [skos:related](http://www.w3.org/2004/02/skos/core#related)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Concept](Concept.md) |
| Domain Of | [Concept](Concept.md) |
| Slot URI | [skos:related](http://www.w3.org/2004/02/skos/core#related) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | W |
| excel_name | er_relatert_til |
| requirement | valgfri |
| separator | , |
| excel_value | concept name (column B) |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:related |
| native | svv:related |




## LinkML Source

<details>
```yaml
name: related
annotations:
  excel_column:
    tag: excel_column
    value: W
  excel_name:
    tag: excel_name
    value: er_relatert_til
  requirement:
    tag: requirement
    value: valgfri
  separator:
    tag: separator
    value: ','
  excel_value:
    tag: excel_value
    value: concept name (column B)
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: skos:related
domain_of:
- Concept
range: Concept
multivalued: true

```
</details></div>
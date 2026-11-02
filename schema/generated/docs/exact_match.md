---
search:
  boost: 5.0
---

# Slot: exact_match 

<div data-search-exclude markdown="1">



URI: [skos:exactMatch](http://www.w3.org/2004/02/skos/core#exactMatch)
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
| Slot URI | [skos:exactMatch](http://www.w3.org/2004/02/skos/core#exactMatch) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | Y |
| excel_name | har_eksakt_samsvar_med |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:exactMatch |
| native | svv:exact_match |




## LinkML Source

<details>
```yaml
name: exact_match
annotations:
  excel_column:
    tag: excel_column
    value: Y
  excel_name:
    tag: excel_name
    value: har_eksakt_samsvar_med
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: skos:exactMatch
domain_of:
- Concept
range: uri
multivalued: true

```
</details></div>
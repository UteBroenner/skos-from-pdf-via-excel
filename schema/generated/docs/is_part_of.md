---
search:
  boost: 5.0
---

# Slot: is_part_of 

<div data-search-exclude markdown="1">



URI: [xkos:isPartOf](http://rdf-vocabulary.ddialliance.org/xkos#isPartOf)
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
| Slot URI | [xkos:isPartOf](http://rdf-vocabulary.ddialliance.org/xkos#isPartOf) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | V |
| excel_name | er_del_av |
| requirement | valgfri |
| excel_value | concept name (column B) |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | xkos:isPartOf |
| native | svv:is_part_of |




## LinkML Source

<details>
```yaml
name: is_part_of
annotations:
  excel_column:
    tag: excel_column
    value: V
  excel_name:
    tag: excel_name
    value: er_del_av
  requirement:
    tag: requirement
    value: valgfri
  excel_value:
    tag: excel_value
    value: concept name (column B)
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: xkos:isPartOf
domain_of:
- Concept
range: Concept
multivalued: true

```
</details></div>
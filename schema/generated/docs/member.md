---
search:
  boost: 5.0
---

# Slot: member 


_Concepts whose main-language scope note names the collection._



<div data-search-exclude markdown="1">



URI: [skos:member](http://www.w3.org/2004/02/skos/core#member)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Collection](Collection.md) | A group of concepts, recorded in the main-language scope note of each member ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Concept](Concept.md) |
| Domain Of | [Collection](Collection.md) |
| Slot URI | [skos:member](http://www.w3.org/2004/02/skos/core#member) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |
| Multivalued | Yes |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_source | scope note sentence: Inngår i samlingen/samlingene … |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:member |
| native | svv:member |




## LinkML Source

<details>
```yaml
name: member
annotations:
  excel_source:
    tag: excel_source
    value: 'scope note sentence: Inngår i samlingen/samlingene …'
description: Concepts whose main-language scope note names the collection.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: skos:member
domain_of:
- Collection
range: Concept
required: true
multivalued: true

```
</details></div>
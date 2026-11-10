---
search:
  boost: 5.0
---

# Slot: collections 


_Container slot for the data file only. Not written to RDF; the collections are written as resources of their own. Built from the scope-note sentence, not from a column._



<div data-search-exclude markdown="1">



URI: [svv:collections](http://example.org/vegvesen/vokabular/def#collections)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ConceptScheme](ConceptScheme.md) | One vocabulary = one Excel workbook (vokabular sheet, rows 1-16) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Collection](Collection.md) |
| Domain Of | [ConceptScheme](ConceptScheme.md) |
| Slot URI | [svv:collections](http://example.org/vegvesen/vokabular/def#collections) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| rdf_skip | True |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | svv:collections |
| native | svv:collections |




## LinkML Source

<details>
```yaml
name: collections
annotations:
  rdf_skip:
    tag: rdf_skip
    value: true
description: Container slot for the data file only. Not written to RDF; the collections
  are written as resources of their own. Built from the scope-note sentence, not from
  a column.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: svv:collections
domain_of:
- ConceptScheme
range: Collection
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
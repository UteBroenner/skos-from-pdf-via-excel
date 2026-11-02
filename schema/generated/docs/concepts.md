---
search:
  boost: 5.0
---

# Slot: concepts 


_Container slot for the data file only. Not written to RDF; the RDF writer emits skos:inScheme on each concept instead._



<div data-search-exclude markdown="1">



URI: [svv:concepts](http://example.org/vegvesen/vokabular/def#concepts)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ConceptScheme](ConceptScheme.md) | One vocabulary = one Excel workbook (vokabular sheet, rows 1-16) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Concept](Concept.md) |
| Domain Of | [ConceptScheme](ConceptScheme.md) |
| Slot URI | [svv:concepts](http://example.org/vegvesen/vokabular/def#concepts) |
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
| self | svv:concepts |
| native | svv:concepts |




## LinkML Source

<details>
```yaml
name: concepts
annotations:
  rdf_skip:
    tag: rdf_skip
    value: true
description: Container slot for the data file only. Not written to RDF; the RDF writer
  emits skos:inScheme on each concept instead.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: svv:concepts
domain_of:
- ConceptScheme
range: Concept
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>
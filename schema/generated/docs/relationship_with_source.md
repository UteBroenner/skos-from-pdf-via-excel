---
search:
  boost: 5.0
---

# Slot: relationship_with_source 


_How the definition relates to its source (SKOS-AP-NO). In Excel the value may also be written with spaces ("derived from source"); the converter writes the hyphenated form._



<div data-search-exclude markdown="1">



URI: [skosno:relationshipWithSource](https://data.norge.no/vocabulary/skosno#relationshipWithSource)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [RelationshipWithSource](RelationshipWithSource.md) |
| Domain Of | [Concept](Concept.md) |
| Slot URI | [skosno:relationshipWithSource](https://data.norge.no/vocabulary/skosno#relationshipWithSource) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | O |
| excel_name | forhold_til_kilde |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skosno:relationshipWithSource |
| native | svv:relationship_with_source |




## LinkML Source

<details>
```yaml
name: relationship_with_source
annotations:
  excel_column:
    tag: excel_column
    value: O
  excel_name:
    tag: excel_name
    value: forhold_til_kilde
description: How the definition relates to its source (SKOS-AP-NO). In Excel the value
  may also be written with spaces ("derived from source"); the converter writes the
  hyphenated form.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: skosno:relationshipWithSource
domain_of:
- Concept
range: RelationshipWithSource

```
</details></div>
---
search:
  boost: 5.0
---

# Slot: uri 


_Concept or scheme URI. For concepts: <scheme URI>/<concept name>, where column B of the workbook holds only the CamelCase concept name (e.g. Rekkverk) and the tools build the URI._



<div data-search-exclude markdown="1">



URI: [svv:uri](http://example.org/vegvesen/vokabular/def#uri)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ConceptScheme](ConceptScheme.md) | One vocabulary = one Excel workbook (vokabular sheet, rows 1-16) |  no  |
| [Concept](Concept.md) | One row in the vokabular sheet (row 23 onwards) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [uri](uri.md) |
| Domain Of | [ConceptScheme](ConceptScheme.md), [Concept](Concept.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |


### Slot Characteristics

| Property | Value |
| --- | --- |
| Identifier | Yes |




## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [ConceptScheme](ConceptScheme.md) | [uri](uri.md) | range | [uri](uri.md) |
| [Concept](Concept.md) | [uri](uri.md) | range | [uri](uri.md) |
| [Concept](Concept.md) | [source](source.md) | range | [uri](uri.md) |
| [Concept](Concept.md) | [exact_match](exact_match.md) | range | [uri](uri.md) |
| [Concept](Concept.md) | [close_match](close_match.md) | range | [uri](uri.md) |
| [Concept](Concept.md) | [in_scheme](in_scheme.md) | range | [uri](uri.md) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | B |
| excel_name | begrep |
| excel_value | CamelCase concept name only |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | svv:uri |
| native | svv:uri |




## LinkML Source

<details>
```yaml
name: uri
annotations:
  excel_column:
    tag: excel_column
    value: B
  excel_name:
    tag: excel_name
    value: begrep
  excel_value:
    tag: excel_value
    value: CamelCase concept name only
description: 'Concept or scheme URI. For concepts: <scheme URI>/<concept name>, where
  column B of the workbook holds only the CamelCase concept name (e.g. Rekkverk) and
  the tools build the URI.'
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
identifier: true
domain_of:
- ConceptScheme
- Concept
range: uri
required: true

```
</details></div>
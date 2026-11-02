---
search:
  boost: 5.0
---

# Slot: hidden_label 


_Discouraged term, e.g. a common misspelling._



<div data-search-exclude markdown="1">



URI: [skos:hiddenLabel](http://www.w3.org/2004/02/skos/core#hiddenLabel)
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
| Slot URI | [skos:hiddenLabel](http://www.w3.org/2004/02/skos/core#hiddenLabel) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | T |
| excel_name | frarådd_term |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:hiddenLabel |
| native | svv:hidden_label |




## LinkML Source

<details>
```yaml
name: hidden_label
annotations:
  excel_column:
    tag: excel_column
    value: T
  excel_name:
    tag: excel_name
    value: frarådd_term
  requirement:
    tag: requirement
    value: valgfri
description: Discouraged term, e.g. a common misspelling.
from_schema: http://example.org/vegvesen/vokabular/def/schema
in_language: nb
rank: 1000
slot_uri: skos:hiddenLabel
domain_of:
- Concept
range: string

```
</details></div>
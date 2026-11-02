---
search:
  boost: 5.0
---

# Slot: editorial_note 

<div data-search-exclude markdown="1">



URI: [skos:editorialNote](http://www.w3.org/2004/02/skos/core#editorialNote)
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
| Slot URI | [skos:editorialNote](http://www.w3.org/2004/02/skos/core#editorialNote) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_column | Q |
| excel_name | merknad_til_etableringmåte |
| requirement | valgfri |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | skos:editorialNote |
| native | svv:editorial_note |




## LinkML Source

<details>
```yaml
name: editorial_note
annotations:
  excel_column:
    tag: excel_column
    value: Q
  excel_name:
    tag: excel_name
    value: merknad_til_etableringmåte
  requirement:
    tag: requirement
    value: valgfri
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: skos:editorialNote
domain_of:
- Concept
range: string

```
</details></div>
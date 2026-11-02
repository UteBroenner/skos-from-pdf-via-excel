---
search:
  boost: 5.0
---

# Slot: main_language 


_BCP 47 tag of the language in which every concept must have a prefLabel and a definition (scheme row "hovedspråk"; default nb). Enforced by SHACL (shapes/cross_row.shacl.ttl)._



<div data-search-exclude markdown="1">



URI: [svv:mainLanguage](http://example.org/vegvesen/vokabular/def#mainLanguage)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ConceptScheme](ConceptScheme.md) | One vocabulary = one Excel workbook (vokabular sheet, rows 1-16) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ConceptScheme](ConceptScheme.md) |
| Slot URI | [svv:mainLanguage](http://example.org/vegvesen/vokabular/def#mainLanguage) |










## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| excel_label | hovedspråk |




### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | svv:mainLanguage |
| native | svv:main_language |




## LinkML Source

<details>
```yaml
name: main_language
annotations:
  excel_label:
    tag: excel_label
    value: hovedspråk
description: BCP 47 tag of the language in which every concept must have a prefLabel
  and a definition (scheme row "hovedspråk"; default nb). Enforced by SHACL (shapes/cross_row.shacl.ttl).
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
slot_uri: svv:mainLanguage
domain_of:
- ConceptScheme
range: string

```
</details></div>
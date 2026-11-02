---
search:
  boost: 2.0
---


# Enum: ConceptStatus 




_Status values from the template's statusliste, mapped to the EU concept-status authority table._



<div data-search-exclude markdown="1">

URI: [svv:ConceptStatus](http://example.org/vegvesen/vokabular/def#ConceptStatus)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| kandidat | concept_status:CANDIDATE |  |
| gjeldende | concept_status:CURRENT |  |
| utdatert | concept_status:DEPRECATED |  |
| forkastet | concept_status:RETIRED |  |




## Slots

| Name | Description |
| ---  | --- |
| [status](status.md) |  |










## Identifier and Mapping Information





### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema






## LinkML Source

<details>
```yaml
name: ConceptStatus
description: Status values from the template's statusliste, mapped to the EU concept-status
  authority table.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
permissible_values:
  kandidat:
    text: kandidat
    meaning: concept_status:CANDIDATE
  gjeldende:
    text: gjeldende
    meaning: concept_status:CURRENT
  utdatert:
    text: utdatert
    meaning: concept_status:DEPRECATED
  forkastet:
    text: forkastet
    meaning: concept_status:RETIRED

```
</details>

</div>
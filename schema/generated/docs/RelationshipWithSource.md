---
search:
  boost: 2.0
---


# Enum: RelationshipWithSource 




_Values of skosno:relationshipWithSource (SKOS-AP-NO). direct-from-source = definition copied or quoted from the source; derived-from-source = paraphrased or derived from the source; self-composed = written without a source._



<div data-search-exclude markdown="1">

URI: [svv:RelationshipWithSource](http://example.org/vegvesen/vokabular/def#RelationshipWithSource)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| self-composed | relationship_with_source_type:self-composed |  |
| derived-from-source | relationship_with_source_type:derived-from-source |  |
| direct-from-source | relationship_with_source_type:direct-from-source |  |




## Slots

| Name | Description |
| ---  | --- |
| [relationship_with_source](relationship_with_source.md) | How the definition relates to its source (SKOS-AP-NO) |










## Identifier and Mapping Information





### Schema Source


* from schema: http://example.org/vegvesen/vokabular/def/schema






## LinkML Source

<details>
```yaml
name: RelationshipWithSource
description: Values of skosno:relationshipWithSource (SKOS-AP-NO). direct-from-source
  = definition copied or quoted from the source; derived-from-source = paraphrased
  or derived from the source; self-composed = written without a source.
from_schema: http://example.org/vegvesen/vokabular/def/schema
rank: 1000
permissible_values:
  self-composed:
    text: self-composed
    meaning: relationship_with_source_type:self-composed
  derived-from-source:
    text: derived-from-source
    meaning: relationship_with_source_type:derived-from-source
  direct-from-source:
    text: direct-from-source
    meaning: relationship_with_source_type:direct-from-source

```
</details>

</div>
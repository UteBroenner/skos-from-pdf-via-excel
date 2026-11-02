# Heklemasker (HEKL): test dataset

Multilingual vocabulary of crochet stitches in nb, en-US, en-GB, de and es (Spain).
It was drafted with Claude and needs expert review. Uncertain terms are marked `[usikker]`
in `skos:editorialNote` and missing ones `[mangler]`. nn labels are left empty on purpose.

The dataset tests these things:

- **Homonyms across language variants:** US and UK English use the same names for different stitches
  (US *double crochet* = UK *treble crochet*). The checker reports them as `VT-LABEL-HOMONYM`.
- **Language tags:** `en-US` and `en-GB` next to `en`.
- **Polyhierarchy:** relief stitches have two broader concepts.
- **Part-whole relations:** stitches are part of shells, V-stitches, rows and granny squares.

`dcat:contactPoint` is empty, because the template requires a `@vegvesen.no` address.

```bash
.venv/bin/python -m vocabtool check datasets/hekling/HEKL-v8.xlsx --out datasets/hekling/out
.venv/bin/python -m vocabtool rdf   datasets/hekling/HEKL-v8.xlsx --out datasets/hekling/out
```

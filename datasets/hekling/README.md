# Heklemasker (HEKL): test dataset

Multilingual vocabulary of crochet stitches and stitch patterns. **Main language: en-US** (`hovedspråk`).
Other languages are nb, en-GB, de and es (Spain), and definitions are in en-US and nb.

- HEKL-0001 to 0036 are basic and special stitches.
- HEKL-0037 to 0060 are stitches and 14 stitch patterns from
  [The Unraveled Mitten, 2022 Stash Busting Crochet Along](https://theunraveledmitten.com/2022/01/25/2022-stash-busting-crochet-along/),
  which uses US terms. Each stitch is linked to a pattern with `xkos:isPartOf` only if the pattern instructions name it.
  Pattern names are the designer's English names. Their definitions are paraphrases marked `[omskrivning]`.
  nb, de and es names are missing (`[mangler]`).
It was drafted with Claude and needs expert review. Uncertain terms are marked `[usikker]`
in `skos:editorialNote` and missing ones `[mangler]`. nn is not used.

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

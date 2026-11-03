# Heklemasker (HEKL): test dataset

Multilingual vocabulary of crochet stitches and stitch patterns. **Main language: en-US** (`hovedspråk`).
Other languages are nb, en-GB, de and es (Spain), and definitions are in en-US and nb.

77 concepts: 49 stitches, structures and working methods, the top concept *stitch pattern*, and 27 stitch patterns.
It was drafted with Claude and needs expert review. Uncertain terms are marked `[usikker]`
in `skos:editorialNote` and missing ones `[mangler]`. nn is not used.

- HEKL-0001 to 0036 are basic and special stitches.
- HEKL-0037 to 0060 are stitches and 14 stitch patterns from
  [The Unraveled Mitten, 2022 Stash Busting Crochet Along](https://theunraveledmitten.com/2022/01/25/2022-stash-busting-crochet-along/),
  which uses US terms. Each stitch is linked to a pattern with `xkos:isPartOf` only if the pattern instructions name it.
  Pattern names are the designer's English names. Their definitions are paraphrases marked `[omskrivning]`.
  nb, de and es names are missing (`[mangler]`).
- HEKL-0061 to 0077 are 4 stitches and 13 patterns from Parts 6–10 of the same crochet-along. They were extracted from
  the saved pages, and each concept links to its part.
  Sections named exactly like an existing stitch (Spike Stitch, Popcorn Stitch, Cluster V-Stitch) are not separate pattern
  concepts. A note on the stitch records them instead.

The dataset tests these things:

- **Homonyms across language variants:** US and UK English use the same names for different stitches
  (UK *treble crochet* = US *double crochet*). The checker reports them as `VT-LABEL-VARIANT` (info), and as
  `VT-LABEL-NOTED` (info) once a scope note documents them. Other clashes are `VT-LABEL-HOMONYM` (warning).
- **Language tags:** `en-US` and `en-GB` next to `en`.
- **Polyhierarchy:** relief stitches have two broader concepts.
- **Part-whole relations:** stitches are part of shells, V-stitches, rows and granny squares.

`dcat:contactPoint` is https://github.com/UteBroenner.

Concept names (column B) are generated from the en-US term, e.g. `SingleCrochet`, which gives the URI
`http://example.org/vegvesen/vokabular/HEKL/SingleCrochet`. Nine stitches whose US name is the UK name of another
stitch carry the suffix `-ENUS`, e.g. `DoubleCrochet-ENUS` (US double crochet = UK treble crochet). The pattern HEKL-0057 is `CrossedDoubleCrochet2`,
because the stitch HEKL-0028 already has `CrossedDoubleCrochet`. This is part of the open stitch-versus-pattern decision.

Every label clash has a draft en-US scope note (column AY) that warns about it and names the other concept's ID.
There are 19 concepts with notes, covering the US/UK cross-overs, Norwegian versus English `st`, Spanish *punto* and *vuelta*,
and the crossed double crochet stitch versus pattern.

Current result: 0 errors and 0 warnings. SHACL passes (1,526 triples).

## Files

| File | Content |
| --- | --- |
| `HEKL-v8.xlsx` | the vocabulary (template v8 with language extension); edit this file |
| `out/HEKL-v8-report.md`, `.json` | check report |
| `out/HEKL-v8-graph.html` | interactive graph; open in a browser |
| `out/HEKL-v8.yaml` | LinkML data |
| `out/HEKL-v8.ttl` | SKOS in RDF Turtle |
| `out/HEKL-v8-shacl-report.md` | LinkML and SHACL validation report |

Regenerate the outputs after editing the workbook:

```bash
.venv/bin/python -m vocabtool check datasets/hekling/HEKL-v8.xlsx --out datasets/hekling/out
.venv/bin/python -m vocabtool rdf   datasets/hekling/HEKL-v8.xlsx --out datasets/hekling/out
```

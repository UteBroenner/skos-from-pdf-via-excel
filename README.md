# vocab-tools

Checks SKOS vocabulary workbooks (Excel template v8, also reads v7) and draws an
interactive graph of `skos:broader`, `xkos:isPartOf` and `skos:related`.
Code lists (`kodeverk` sheet) are ignored.

Requires Python 3.10+ and `openpyxl`.

## Commands

Validate a workbook. This writes a report (`.md` and `.json`) and a graph page (`.html`) to `out/`:

```bash
python -m vocabtool check path/to/workbook.xlsx --out out
```

The exit code is 1 if there are errors, so the command can be used as a gate.

Migrate a v7 workbook into the v8 template. This assigns IDs `<kortnavn>-0001…` and
rewrites relations from `vok:X` to IDs:

```bash
python -m vocabtool migrate samples/N101-v7.xlsx --template templates/SKOS-Excel-mal-v8-for-import.xlsx --out out/N101-v8.xlsx
```

Relation targets that are not in the workbook (for example `vok:Veg`) are kept
as written and listed, so they show up as `VT-REF-FORMAT` errors in v8.

## Conventions assumed for v8

- Column A `dct:identifier` holds the row key `<kortnavn>-NNNN` (kortnavn: max 4 letters or digits).
- `skos:broader`, `xkos:isPartOf` and `skos:related` contain **IDs**, separated by commas.
- Header row = the row with `skos:prefLabel@nb`. In v8 the following row holds the technical names.

## Rules

| Rule | Severity | Check |
| --- | --- | --- |
| VT-ID-FORMAT | error | ID matches `<kortnavn>-NNNN` (v8) |
| VT-ID-DUPLICATE | error | ID unique |
| VT-REQ-LABEL / VT-REQ-DEF | error | prefLabel@nb and definition@nb present |
| VT-REF-FORMAT | error | relation values are IDs (v8) |
| VT-REF-SELF | error | no relation to itself |
| VT-CYCLE-BROADER / VT-CYCLE-PARTOF | error | no cycles |
| VT-RELATED-CLASH | error | `related` not combined with a broader/narrower path (SKOS integrity) |
| VT-REF-DANGLING | warning | relation target exists in the workbook |
| VT-T1-ISOLATED | warning | Tier 1 concept has at least one link |
| VT-T1-BROADER-NON-T1 | warning | broader of a Tier 1 concept is Tier 1 (OWL rule O4) |
| VT-LABEL-DUPLICATE | warning | prefLabel@nb unique |
| VT-LABEL-CASE | warning | prefLabel@nb lowercase, except acronyms (S05) |
| VT-LABEL-GROUPING | warning | heuristic: label lists several items ("… og …") and has ≥2 narrower concepts, so it is probably a table heading |
| VT-STATUS / VT-STATUS-LITERAL | warning | status is one of kandidat, gjeldende, utdatert, forkastet, written as a plain value |
| VT-TIER-INVALID | warning | tier is 1, 2 or 3 |
| VT-CONTACT | warning | contactPoint present |
| VT-TIER-EMPTY / VT-NN-MISSING | info | expected gaps (source concepts; nn left for the expert) |

## Graph page

The graph page is a single HTML file and loads no JavaScript libraries.
Google Fonts are optional and fall back to system fonts when offline.
In the page you can filter by relation type and tier, search by label or ID,
show a concept's 1–3 step neighbourhood, and mark validation findings.
The side panel lists all relations, including inverse ones (narrower, has part)
and targets that are missing from the workbook.

## Layout

```
vocabtool/reader.py          read v7/v8 workbooks into records
vocabtool/validate.py        rules above
vocabtool/migrate.py         v7 -> v8
vocabtool/graph.py           graph data + page
vocabtool/graph_template.html
templates/                   Excel template v8
samples/                     N101 and V440 (v7)
```

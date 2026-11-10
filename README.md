# General
This repository holds tools and instructions / skills for Claude.ai / Claude Code to extract concepts from a source (e.g. PDF).
It works with an Excel template that will be reviewed by humans. The spreadsheet holds the information in columns that 
are compliant with the Norwegian standard for concept descriptions https://fellesdatakatalog.digdir.no/specification/skos-ap-no-begrep,
i.e. concepts are described in the two Norwegian languages with a set of mandatory properties.
The main language can be changed per vocabulary (`hovedspråk`); the crochet example uses US English.
The attributes `skos:broader`, `xkos:isPartOf` and `skos:related` create a taxonomy, while `skos:altLabel`, `skos:hiddenLabel`, `skos:exactMatch` and `skos:closeMatch` make a thesaurus 
that might be used further in a simple information model. 

After review by technical experts these spreadsheets can be converted to RDF for machine readability and further
development into ontologies. 

## Repository contents

| Folder | Content | Status |
| --- | --- | --- |
| `vocabtool/` | Python tools: check, v7→v8 migration, graph, LinkML/RDF conversion, language columns, clash notes | in repository |
| `schema/` | LinkML schema for template v8, generated artefacts (JSON Schema, Pydantic, SHACL, OWL, docs), cross-row SHACL rules | in repository |
| `templates/` | Empty Excel templates: v8 (master), v8 with language extension, and v7 (previous version), see `templates/README.md` | in repository |
| `datasets/hekling/` | Example vocabulary: 77 crochet stitches and stitch patterns, main language en-US, with check reports, graph and RDF in `out/` | in repository |
| `instructions/` | Extraction instructions (project instructions, prompt template, SKOS field instructions, RDF conversion rules) | **not yet added** |
| `samples/`, `out/` | Your own (e.g. Vegvesen) workbooks and their outputs | local only, ignored by git |

## vocab-tools
Checks SKOS vocabulary workbooks and draws an
interactive graph of `skos:broader`, `xkos:isPartOf` and `skos:related`.

Apart from the crochet example, vocabulary data is not part of this repository. Put your workbooks in `samples/`;
outputs are written to `out/`. Both top-level folders are ignored by git.

Requires Python 3.10+. `check` and `migrate` need only `openpyxl`. The LinkML/RDF route needs `requirements.txt`:

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

### Commands

Validate a workbook. This writes a report (`.md` and `.json`) and a graph page (`.html`) to `out/`:

```bash
python -m vocabtool check path/to/workbook.xlsx --out out
```

The exit code is 1 if there are errors, so the command can be used as a gate.

Migrate a v7 workbook into the v8 template. This keeps the v7 concept name in column B (`vok:Rekkverk` → `Rekkverk`)
and rewrites relations from `vok:X` to names (`X`):

```bash
python -m vocabtool migrate samples/N101-v7.xlsx --template templates/SKOS-Excel-mal-v8-for-import.xlsx --out out/N101-v8.xlsx
```

Relation targets that are not in the workbook are kept as names and listed. The checker reports them as
`VT-REF-DANGLING` (they may be concepts of another vocabulary).


Fill empty concept names (column B) from the main-language term, in CamelCase
(`rekkverk` → `Rekkverk`, `brystningshøyde` → `Brystningshoyde`, `skråstagbru` → `Skraastagbru`,
`CE-merket produkt` → `CEMerketProdukt`, `single crochet` → `SingleCrochet`). æ → ae, ø → o, å → aa;
acronyms written in capitals stay in capitals:

```bash
python -m vocabtool uri path/to/workbook.xlsx
```

Rename a concept. This changes column B and every relation and note that refers to it:

```bash
python -m vocabtool rename path/to/workbook.xlsx OldName NewName
```

Existing names are kept, and `--overwrite` regenerates all of them. If two concepts would get the same name,
the second gets a number (`Name2`) and the command lists it, so you can choose a better name.

Stretch the Excel table `begrepsliste`, the formatting (wrapped, top-aligned), conditional formatting and
data validation to all rows and columns in use, and write the formulas for column A and `endringshash`.
Power Automate reads only what is inside the table.
The `tier` column (always last) stays outside the table.
`migrate` and `uri` do this automatically:

```bash
python -m vocabtool fit path/to/workbook.xlsx
```

Convert to LinkML data and RDF Turtle, and validate with LinkML and SHACL (see `schema/README.md`):

```bash
.venv/bin/python -m vocabtool rdf out/N101-v8.xlsx --out out/rdf
```

Add language columns to the template. They are inserted after column AM, and `tier` moves to the last column,
outside the Excel table. It is internal and is not imported. Columns A–AM keep their letters:

```bash
.venv/bin/python -c "from vocabtool.template_ext import extend_template as e; print(e('templates/SKOS-Excel-mal-v8-for-import.xlsx', 'templates/SKOS-Excel-mal-v8-lang-ext.xlsx', ['en-US','en-GB','de','es'], ['en-US']))"
```

The extended template also has a scheme row `hovedspråk` (main language; default `nb`).
Every concept needs a prefLabel and a definition in that language, and the label checks
(duplicates, lowercase, grouping) use it. The nn check only applies when the main language is nb.

Any column headed `skos:prefLabel@<tag>`, `skos:altLabel@<tag>`, `skos:definition@<tag>` or `skos:scopeNote@<tag>` is read automatically.

`vocabtool/clash_notes.py` drafts English scope notes for label clashes, for example
"Caution: 'dc' is the UK abbreviation of this concept and the US abbreviation of DoubleCrochet (double crochet)."
Once a scope note names the other concept, the checker reports the clash as `VT-LABEL-NOTED` (info).
The LinkML schema needs a slot per language (see `schema/svv_vokabular.yaml`, section "language extension").

## Conventions assumed for v8

- **Column B (concept name) is the key.** Relations use it, and column A `dct:identifier` is the formula
  `<kortnavn>-<name>` (e.g. `N101-Rekkverk`), so nothing has to be generated or converted.
  Use `vocabtool rename` to rename a concept; it updates the relations and notes that point to it.
- Column B holds only the concept name in CamelCase (letters and digits), e.g. `Rekkverk`.
  The tools build the URI from it: ConceptScheme URI (cell B1, `…/vokabular/<kortnavn>`) + `/` + name,
  e.g. `http://example.org/vegvesen/vokabular/N101/Rekkverk`. The vocabulary segment keeps equal names
  in different vocabularies apart.
- Layout of the master template (`templates/SKOS-Excel-mal-v8-for-import.xlsx`): scheme rows 14–18 (B14 `kortnavn`,
  B15 title, B16 `dct:creator`), requirement row 20, description row 21, property row 23, technical names in row 24
  (the Excel table header), data from row 25. Column AD (`opprettet_av`) is hidden and filled by formula from B16.
  `endringshash` (formula: `TEXTJOIN` of the row content without ID, dates and persons) is the last column inside
  the table, and `tier` is the last column, outside it. `vocabtool fit` writes both formulas for all table rows.

## Power Automate import (planned design)

The import stamps `dato_sist_endret` / `sist_endret_av` only on concepts whose content changed:

1. Trigger: the workbook is created or changed in the SharePoint library. The file's *Modified By* is the editor.
2. For each row of the table `begrepsliste`, find the List item by `intern_identifikator`:
   - **no item:** create it; `dato_opprettet` = today.
   - **`endringshash` differs:** update it; `dato_sist_endret` = today, `sist_endret_av` = the editor.
   - **`endringshash` equal:** skip.

Store `endringshash` in a multi-line text column. The value is long, and single-line text holds only 255 characters.

If two people edit the same file between imports, every change is attributed to the last one,
so use one reviewer per file/domain at a time.
- `skos:broader`, `xkos:isPartOf` and `skos:related` contain **concept names** (column B), separated by commas.
- Header row = the row with `skos:prefLabel@nb`. In v8 the following row holds the technical names.
- Code lists (`kodeverk` sheet) are not read.

## Rules

| Rule | Severity | Check |
| --- | --- | --- |
| VT-ID-FORMAT | error | column A is `<kortnavn>-<concept name>` (v8) |
| VT-ID-DUPLICATE | error | row key unique (v7; in v8 see VT-URI-DUPLICATE) |
| VT-KORTNAVN | error | kortnavn: letters, digits and hyphens, starting with a letter or digit (e.g. `N101`, `crochet-us`) |
| VT-URI-MISSING / VT-URI-FORMAT / VT-URI-DUPLICATE | error | concept name in column B present, CamelCase letters and digits, unique (S03) |
| VT-URI-LABEL | info | concept name differs from the CamelCase form of the main-language term |
| VT-REQ-LABEL / VT-REQ-DEF | error | prefLabel and definition present in the main language (`hovedspråk`, default nb) |
| VT-REF-FORMAT | error | relation values are concept names (v8) |
| VT-REF-SELF | error | no relation to itself |
| VT-CYCLE-BROADER / VT-CYCLE-PARTOF | error | no cycles |
| VT-RELATED-CLASH | error | `related` not combined with a broader/narrower path (SKOS integrity) |
| VT-REF-DANGLING | warning | relation target exists in the workbook |
| VT-T1-ISOLATED | warning | Tier 1 concept has at least one link |
| VT-T1-BROADER-NON-T1 | warning | broader of a Tier 1 concept is Tier 1 (OWL rule O4) |
| VT-LABEL-DUPLICATE | warning | main-language prefLabel unique |
| VT-LABEL-HOMONYM | warning | same term (any label or abbreviation, any language) on different concepts, e.g. US/UK *double crochet* |
| VT-LABEL-NOTED | info | a label clash (homonym, variant or duplicate) that the concept's scope note documents by naming the other concept's ID |
| VT-LABEL-VARIANT | info | same term means different concepts in two regional variants (en-US vs en-GB); this is the difference the vocabulary documents |
| VT-LABEL-CASE | warning | main-language prefLabel lowercase, except acronyms (S05) |
| VT-LABEL-GROUPING | warning | heuristic: label lists several items ("… og …") and has ≥2 narrower concepts, so it is probably a table heading |
| VT-STATUS / VT-STATUS-LITERAL | warning | status is one of kandidat, gjeldende, utdatert, forkastet, written as a plain value |
| VT-TIER-INVALID | warning | tier is 1, 2 or 3 |
| VT-CONTACT | warning | contactPoint present |
| VT-TIER-EMPTY / VT-NN-MISSING | info | expected gaps (source concepts; nn left for the expert, only when the main language is nb) |

## Graph page

The graph page is a single HTML file and loads no JavaScript libraries.
Google Fonts are optional and fall back to system fonts when offline.
In the page you can filter by relation type and tier, search by label or concept name,
show a concept's 1–3 step neighbourhood, and mark validation findings.
The side panel lists all relations, including inverse ones (narrower, has part)
and targets that are missing from the workbook.
With several label languages, a selector switches the node labels (e.g. en-US / en-GB), and the side panel
shows all labels, definitions and scope notes.

## Layout

```
vocabtool/reader.py          read v7/v8 workbooks into records
vocabtool/validate.py        rules above
vocabtool/migrate.py         v7 -> v8
vocabtool/graph.py           graph data + page
vocabtool/graph_template.html
vocabtool/linkml_rdf.py      Excel -> LinkML data -> RDF, SHACL fixes
vocabtool/template_ext.py    add language columns to the template
vocabtool/clash_notes.py     draft scope notes for label clashes
vocabtool/uri.py             concept names (CamelCase) and URIs
vocabtool/rename.py          rename a concept and its references
schema/                      LinkML schema, generated artefacts, cross-row SHACL
templates/                   empty templates: v8 (master), v8 with language extension, v7
datasets/hekling/            example dataset: crochet stitches and patterns (en-US main; nb, en-GB, de, es)
datasets/hekling/out/        its check report, graph, YAML and Turtle
samples/                     your workbooks (not in git)
out/                         generated output (not in git)
```

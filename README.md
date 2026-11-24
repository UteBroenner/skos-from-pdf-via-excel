# SKOS vocabularies from PDF via Excel

This repository holds tools and instructions for building controlled vocabularies (SKOS) from sources such as
handbooks in PDF, OWL ontologies and existing vocabularies, with Claude.ai, Claude Code or another LLM doing the
extraction. Subject-matter experts review the results in an Excel template. Its columns follow the Norwegian standard
for concept descriptions, [SKOS-AP-NO-Begrep](https://fellesdatakatalog.digdir.no/specification/skos-ap-no-begrep):
concepts are described in bokmål and nynorsk with a set of mandatory properties. The main language can be changed per
vocabulary (`hovedspråk`); the crochet example uses US English.

`skos:broader`, `xkos:isPartOf` and `skos:related` build a taxonomy; `skos:altLabel`, `skos:hiddenLabel`,
`skos:exactMatch` and `skos:closeMatch` make it a thesaurus that can feed a simple information model. After review,
the workbooks are converted to RDF (SKOS in Turtle), validated with SHACL, and can be developed further into ontologies.

- Current state, decisions and next steps: [`docs/status.md`](docs/status.md)
- API reference of the Python tools, generated from the code: [`docs/api/`](docs/api/README.md)
- Templates and their value lists and colours: [`templates/README.md`](templates/README.md)
- LinkML schema and the SHACL fixes: [`schema/README.md`](schema/README.md)

## Repository contents

| Folder | Content | Status |
| --- | --- | --- |
| `vocabtool/` | Python tools: check, migration v7 → v9, graph page, LinkML/RDF conversion, template upkeep, OWL import, extraction from text | in repository |
| `schema/` | LinkML schema for template v9, generated artefacts (JSON Schema, Pydantic, SHACL, OWL, docs), cross-row SHACL rules | in repository |
| `templates/` | Empty Excel templates: v9 (master), v9 with language extension, and v7 (previous version) | in repository |
| `datasets/hekling/` | Example vocabulary: 77 crochet stitches and stitch patterns, main language en-US, with check report, graph and RDF in `out/` | in repository |
| `docs/` | Project status (`status.md`) and the API reference (`api/`, generated) | in repository |
| `tools/` | `gen_api_docs.py`: writes `docs/api/` from the docstrings | in repository |
| `tests/` | Tests of the value lists and the type column | in repository |
| `.github/workflows/` | `docs.yml`: checks that `docs/api/` is up to date and runs the tests, on every push and pull request | in repository |
| `instructions/` | Extraction instructions: project instructions and SKOS field instructions (v9), prompt template | **not yet added** (kept locally) |
| `samples/`, `out/` | Your own (e.g. Statens vegvesen) workbooks and their outputs | local only, ignored by git |

Apart from the crochet example, vocabulary data is not part of this repository. Put your workbooks in `samples/`;
outputs are written to `out/`. Both folders are ignored by git.

## Installation

Python 3.10 or later (tested with 3.12 and 3.13). Most commands need only `openpyxl`; `rdf` (LinkML, SHACL) and
`owl-import` (rdflib) need everything in `requirements.txt`. The versions there are pinned to the ones the tools were
tested with; LinkML changes between releases, and the project works around some of its gaps in its own code (see
`schema/README.md`), so test the whole route (`check`, `rdf`, the tests) before raising a version:

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Run the tools as `python -m vocabtool <command>`; `python -m vocabtool <command> --help` lists the options.

## Commands

| Command | Purpose | Needs |
| --- | --- | --- |
| `check` | validate a workbook (VT rules); report (`.md`, `.json`) and graph page (`.html`) | openpyxl |
| `migrate` | copy a v7 workbook into the v9 template | openpyxl |
| `uri` | fill empty concept names (column B) from the main-language term | openpyxl |
| `rename` | rename concepts or a collection, with every reference | openpyxl |
| `fit` | write the formulas, stretch the Excel table, write the value lists and dropdowns | openpyxl |
| `rdf` | LinkML data (`.yaml`), SKOS Turtle (`.ttl`), LinkML and SHACL report | requirements.txt |
| `owl-import` | add the classes of OWL ontologies as concepts, merging with existing ones | requirements.txt |
| `extract prepare` / `extract collect` | extraction from text, one LLM agent per chapter | openpyxl |
| `set-fields` | write reviewed values (e.g. definitions) into concepts by name, from JSON | openpyxl |

### check

```bash
python -m vocabtool check path/to/workbook.xlsx --out out
```

Writes `<name>-report.md`, `<name>-report.json` and `<name>-graph.html` to `--out`. The exit code is 1 if there are
errors, so the command can be used as a gate. The rules are listed under [Rules](#rules).

### migrate

```bash
python -m vocabtool migrate samples/N101-v7.xlsx --template templates/SKOS-Excel-mal-v9-for-import.xlsx --out out/N101-v9.xlsx
```

Keeps the v7 concept name in column B (`vok:Rekkverk` → `Rekkverk`) and rewrites relations from `vok:X` to names
(`X`); `skos:changeNote` moves to `adms:versionNotes`. Relation targets that are not in the workbook are kept as names
and listed; the checker reports them as `VT-REF-DANGLING` (they may be concepts of another vocabulary). The map
v7 URI → name is written to `<out>.namemap.json`. Only real v7 files are accepted.

### uri

```bash
python -m vocabtool uri path/to/workbook.xlsx
```

Fills empty concept names in column B from the main-language term, in CamelCase (`rekkverk` → `Rekkverk`,
`brystningshøyde` → `Brystningshoyde`, `skråstagbru` → `Skraastagbru`, `CE-merket produkt` → `CEMerketProdukt`,
`single crochet` → `SingleCrochet`). The rule is described under [Conventions](#conventions-template-v9).
Existing names are kept; `--overwrite` regenerates all of them. If two concepts would get the same name, the second
gets a number (`Name2`) and the command lists it, so you can choose a better name.

### rename

```bash
python -m vocabtool rename path/to/workbook.xlsx OldName NewName [OldName2 NewName2 …]
python -m vocabtool rename path/to/workbook.xlsx --collection "Old name" "New name"
```

A concept rename changes column B and every relation and note (scope and editorial notes, any language) that refers
to the concept. A collection rename changes the name in every collection sentence (see [Collections](#collections))
and nothing else; a concept rename leaves those sentences alone.

### fit

```bash
python -m vocabtool fit path/to/workbook.xlsx
```

- Writes the formulas in column A (identifier), B (concept name, only where empty or already a formula),
  `opprettet_av` and `endringshash`.
- Stretches the Excel table `begrepsliste`, the formatting (top-aligned, wrapped; the hash column is not wrapped, so
  rows stay one line high), conditional formatting and dropdowns to all rows and columns in use. Power Automate reads
  only what is inside the table. The `type` column (always last) stays outside the table.
- Writes the value lists and dropdowns (see below). `migrate`, `uri` and the other tools that save a workbook do the
  same automatically.

`fit` does not change colours. When the tools add columns (language columns, `endringshash`), they colour the
requirement row, the property row and the technical-name row of those columns by the requirement level, using the
colours the template uses most for that level (theme colours, so the branding is kept). The template's own columns
keep their colours, which deliberately differ in places (see `templates/README.md`).

Value lists: every tool that saves a workbook writes the dropdowns for målgruppe (M), forhold til kilde (O), status
(AI) and `type` again, with the values in the dropdown itself, and the hidden sheet `lister` with the codes and URIs,
from `vocabtool/lists.py`. openpyxl, which the tools use, drops dropdowns stored in Excel's newer format; the tools
write them in the classic format. Recognised values are written as the list label (`direct-from-source` →
`sitat fra kilde`).

### rdf

```bash
.venv/bin/python -m vocabtool rdf out/N101-v9.xlsx --out out/rdf
```

Converts the workbook to LinkML data (`.yaml`) and SKOS in RDF Turtle (`.ttl`, with `skos:Collection`), and validates
it with LinkML and SHACL, including the cross-row rules (`<name>-shacl-report.md`). Enum values become IRIs (status,
målgruppe, forhold til kilde). Persons (`begrepseier`, `opprettet_av`, `sist_endret_av`) are not converted; only
`dcat:contactPoint` is. See `schema/README.md`. The exit code is 1 if SHACL does not conform.

### Language extension

```bash
.venv/bin/python -c "from vocabtool.template_ext import extend_template as e; print(e('templates/SKOS-Excel-mal-v9-for-import.xlsx', 'templates/SKOS-Excel-mal-v9-lang-ext.xlsx', ['en-US','en-GB','de','es'], ['en-US'], scope_langs=['en-US']))"
```

Adds language columns to the template. They are inserted in front of `endringshash`, which stays the last column of
the table, and `type` stays the last column, outside the Excel table. Columns A–AM keep their letters.

The extended template also has a scheme row `hovedspråk` (main language; default `nb`). Every concept needs a
prefLabel and a definition in that language, and the label checks (duplicates, lowercase, grouping) use it. The nn
check only applies when the main language is nb. Any column headed `skos:prefLabel@<tag>`, `skos:altLabel@<tag>`,
`skos:definition@<tag>` or `skos:scopeNote@<tag>` is read automatically; the LinkML schema needs a slot per language
(see `schema/svv_vokabular.yaml`, section "language extension").

`vocabtool/clash_notes.py` drafts English scope notes for label clashes, for example "Caution: 'dc' is the UK
abbreviation of this concept and the US abbreviation of DoubleCrochet (double crochet)." Once a scope note names the
other concept, the checker reports the clash as `VT-LABEL-NOTED` (info).

### owl-import

Add the classes of OWL ontologies (Turtle) as concepts to a workbook. Classes that are already concepts are merged:

```bash
python -m vocabtool owl-import V440.xlsx v440-owl.ttl v440-brudata-owl.ttl --out V440-owl.xlsx --contact datagovernance@vegvesen.no --type 1
```

Start a new vocabulary from the empty template, and copy definitions from another vocabulary where a label matches:

```bash
python -m vocabtool owl-import templates/SKOS-Excel-mal-v9-for-import.xlsx v441-owl.ttl --out V441.xlsx --kortnavn V441 --title "Hb V441" --link V440-owl.xlsx
```

- **Merge:** a class whose Norwegian label (or an alt label) is already in the workbook is merged into that concept,
  when only one class in the file uses the label. The concept gets the class IRI in `skos:exactMatch`; code and English
  label are filled only where empty, and a different code is listed as a conflict in the log, never overwritten. If the
  OWL parent differs from the concept's broader, both are kept in `skos:broader` and the editorial note says
  "[fagekspert] To overbegreper: … (arbeidsbok) og … (OWL-hierarki). Behold ett eller begge."
- **Reviewed merges:** `--merge-map map.json` (`{"<class IRI>": "<concept name>"}`) merges spelling or wording
  variants, e.g. classes with the same code. The class label is recorded in the editorial note.
- **New concepts:** label from `rdfs:label@no` (first letter lower case unless an acronym) and `@en`; `kode` →
  `skos:notation`; parent class → `skos:broader`; class IRI → `skos:exactMatch`; source = the ontology; editorial note
  with chapter and section and `[mangler] definisjon`. A label used by several classes gets the parent as qualifier
  ("fundament, pilar"). A class without a label gets a term from its IRI, flagged in the editorial note.
- **`--type 1`:** sets the type of new concepts (existing concepts keep theirs). Classes from an ontology are type 1.
  The former name `--tier` still works.
- **`--derive-code-definitions`:** a new code entry (a class with `kode`) without another definition gets one built
  from the code table, e.g. "kodeverdi 59 under «buebru og hvelvbru» i V440 (kap. V-6, avsnitt V-6.1)", with
  `relationshipWithSource` `derived-from-source` and `[avledet]` in the editorial note. The checker lists these as
  `VT-DEF-DERIVED` (info), so an expert can replace them with a real definition.
- **`--link`:** a new concept whose label matches one concept with a definition in the other workbook gets
  `skos:exactMatch` to it, its definition copied and that concept as source (`direct-from-source`).
- **Skipped:** deprecated classes and the technical root (the single top class of a file); `--keep-root` keeps the
  root. Code values (individuals) and properties are not imported.
- The rows are added in hierarchy order (parent first, siblings by code), and the same input always gives the same
  workbook. The log (`<out>.owl-import.json` or `--log`) lists merged, new, skipped and linked classes and the
  conflicts.

### extract

Extract concepts from a text file (e.g. a PDF converted to TXT), one LLM agent per chapter:

```bash
python -m vocabtool extract prepare source.txt --out work/ --instructions SKOS-felt-instruksjer-v9.md --kortnavn V441 --title "N-V441 Bruinspeksjon"
```

`prepare` splits the text into chunks and writes, per chunk, the text, a prompt and an entry in `work/manifest.json`
with its size.

- **Headings:** numbered headings with or without a space after the number ("5Tiltak", "5 Tiltak",
  "2.5.3 Hovedinspeksjon"), and appendices starting with one of `--appendix-words` (default
  `Tillegg,Vedlegg,Appendix,Annex`) followed by a letter, with sections "B.3". Lines ending in a page number are
  table-of-contents entries; lines such as "1. Lov om …" or ending with a full stop are list items, not headings.
- **Order:** a chapter is accepted only after the previous one (5 after 4), a section only inside its chapter and after
  the previous section. If chapter 1 appears again before chapter 2, everything before it is dropped (foreword, table
  of contents); numbered lines in tables ("4 Aluminium" after chapter 7) are ignored. `--start-line N` skips the start
  explicitly.
- **Size:** `--level 2` splits at sections (5.2, B.3) instead of chapters; `--min-chars N` merges short sections into
  the next one of the same chapter. `--only ch5 appB.3` limits the run to some chunks.
- **Prompt:** the chunk, the field instructions given with `--instructions`, the terms of `--known` workbooks (so the
  agent does not create them again) and the record format. `--prompt-template FILE` replaces the built-in Norwegian
  prompt; it uses the placeholders
  `{title_doc} {kortnavn} {number} {title} {text} {known} {instructions} {fields} {result_path}`.

Each prompt is then given to one agent, which writes a JSON list of records to `work/results/<chapter>.json` (term,
section, verbatim quote, definition, quote/paraphrase/none, type, alt labels, code, broader/isPartOf/related by term,
cue words, uncertainty). In Claude Code the coordinating session starts one subagent per chapter; chapters that
already have a result are skipped, so a run can stop (e.g. at a usage limit) and continue later.

```bash
python -m vocabtool extract collect work/manifest.json templates/SKOS-Excel-mal-v9-for-import.xlsx --out V441.xlsx --source https://… --contact …
```

`collect` checks every record against the format and rejects it if its quote is not in the chapter. A definition
marked as a quote that is not verbatim is kept as a paraphrase. Names, relations (terms resolved to names), source,
`relationshipWithSource`, flags (`[kilde]`, `[omskrivning]`, `[mangler]`, `[usikker]`), status, contact point and date
are written by code. Terms are compared regardless of case, spaces, hyphens and slashes ("ROS-analyse" =
"ROS analyse").

- **Existing terms** are not added again. If the existing concept has no definition and the record has one, it is
  written to `<out>.suggestions.json` in `set-fields` format, for review.
- **Repeated terms** in one run are added once.
- **`--link v9.xlsx …`:** a new term that matches exactly one concept in another vocabulary gets `skos:exactMatch` to
  it; if that concept has a definition from a source (not `[avledet]`), the definition is copied with that concept as
  source (merge rule). Relation targets found only in a linked vocabulary are reported and noted as `[usikker]`.

The report (`<out>.extract-report.md`) lists accepted, rejected, existing, repeated and linked terms, quote
definitions kept as paraphrase, and relations that could not be resolved.

### set-fields

Write reviewed values, e.g. definitions taken from a handbook, into concepts by name:

```bash
python -m vocabtool set-fields V441.xlsx definitions-V441.json
```

The JSON maps concept names to fields:
`{"Nivellement": {"def_nb": "…", "source": "https://…", "relationship_with_source": "derived-from-source"}}`.
A field name ending in `+` appends to the current value (`"editorial_note+": "[merknad] …"`). Unknown names or fields
stop the command before anything is written; column A, column B and the formula columns are never written. Keep the
JSON next to the workbook: after a new `owl-import`, run `set-fields` again to restore the reviewed values.

## Conventions (template v9)

v9 has the same columns as v8; the tools read v7, v8 and v9 files.

- **Column B (concept name) is the key.** Relations use it, and column A `dct:identifier` is the formula
  `<kortnavn>-<name>` (e.g. `N101-Rekkverk`), so nothing has to be generated or converted. Column A stays this short
  form; the full URI is only built in the RDF. Use `vocabtool rename` to rename a concept.
- **Concept names:** only letters and digits, in CamelCase, e.g. `Rekkverk`. In the template column B is a formula over
  the bokmål term in column C (Excel 365/2021, `LET`; up to 20 words), following the same rule as the tools: æ → ae,
  ø → o, å → aa, ä → ae, ö → oe, ü → ue, ß → ss and common accents removed; words split at spaces and punctuation;
  each word capitalised, the rest lower case; words written fully in capitals (acronyms) kept (`CE-merket produkt` →
  `CEMerketProdukt`). A name typed into B replaces the formula, e.g. for a qualifier or when two terms give the same
  name. Files saved by the tools have no cached formula result, so the tools compute the name from the term in the
  same way.
- **URIs:** ConceptScheme URI (cell B1, `…/vokabular/<kortnavn>`) + `/` + name, e.g.
  `http://example.org/vegvesen/vokabular/N101/Rekkverk`. The vocabulary segment keeps equal names in different
  vocabularies apart.
- **Relations:** `skos:broader`, `xkos:isPartOf` and `skos:related` contain concept names (column B), separated by
  commas.
- **No prefixes in the Excel table:** concept names stand alone (`Rekkverk`, not `vok:Rekkverk`), in relations,
  `dct:subject` and notes. The hidden PREFIX rows above the table stay; the machine-readable artefacts (LinkML schema
  and data, RDF Turtle) use prefixes as usual. `kode:` references to code lists stay until code lists are decided.
- **Layout of the master template** (`templates/SKOS-Excel-mal-v9-for-import.xlsx`): scheme rows 14–18 (B14
  `kortnavn`, B15 title, B16 `dct:creator`), requirement row 20, description row 21, property row 23, technical names
  in row 24 (the Excel table header), data from row 25. The header row is found as the row with `skos:prefLabel@nb`.
  Column AD (`opprettet_av`) is hidden and filled by formula from B16 for rows with a name. `endringshash` (formula:
  `TEXTJOIN` of the row content without ID, dates and persons) is the last column inside the table, and `type` is the
  last column, outside it.
- **type** (called `tier` before 24 November 2026): 1 = physical objects, spatial concepts and measurable properties;
  2 = processes and states; 3 = normative requirements. Internal, not imported. Files with a `tier` header are still
  read, and the tools rename the header when they save.
- **Value lists** on the hidden sheet `lister`: status (AI), målgruppe (M), forhold til kilde (O); see
  `templates/README.md`. The template has no `kodeverk` sheet for now; the `kodeverk` and `lister` sheets are not read
  as concepts.
- **Persons** (`begrepseier` AB, property `prov:Person`; `opprettet_av` AD, `dct:creator`; `sist_endret_av` AF,
  `dct:contributor`) are names in Excel and are not converted to RDF; only `dcat:contactPoint` is. The intended
  properties are documented in the schema.

## Collections

A collection (`skos:Collection`) is recorded only in the main-language scope note of each member concept, with a
fixed sentence:

> Inngår i samlingen Hoveddata.
> Inngår i samlingene Skader, Inspeksjon.

- Use `samlingen` for one collection and `samlingene` for several. Separate names with commas, not "og", because "og"
  can be part of a name (`Arkiv og dokumentasjon`). End the sentence with a full stop.
- Write the name as you would say it. The tools build the URI from its CamelCase form:
  `…/vokabular/<kortnavn>/samling/Hoveddata`. The name as written becomes the collection's `skos:prefLabel`.
- Only the main-language scope note is read (column `skos:scopeNote@<hovedspråk>`). The sentence stays in the
  published scope note, so readers see it too.
- Collections are unordered and not nested, and have no definition, source or status of their own. Code lists can
  still be sorted by `skos:notation`.
- `dct:subject` is for subject areas only, not for collections.

The checker lists each collection with its members (`VT-COLL-MEMBERS`) and reports likely mistakes: one member only,
almost identical names, one name spelled two ways, a sentence it cannot read, and the sentence in a scope note of
another language. `rdf` writes the collections with `skos:member`.

## Power Automate import (planned design)

The import stamps `dato_sist_endret` / `sist_endret_av` only on concepts whose content changed:

1. Trigger: the workbook is created or changed in the SharePoint library. The file's *Modified By* is the editor.
2. For each row of the table `begrepsliste`, find the List item by `intern_identifikator`:
   - **no item:** create it; `dato_opprettet` = today.
   - **`endringshash` differs:** update it; `dato_sist_endret` = today, `sist_endret_av` = the editor.
   - **`endringshash` equal:** skip.

Store `endringshash` in a multi-line text column. The value is long, and single-line text holds only 255 characters.
If two people edit the same file between imports, every change is attributed to the last one, so use one reviewer
per file/domain at a time.

## Rules

| Rule | Severity | Check |
| --- | --- | --- |
| VT-ID-FORMAT | error | column A is `<kortnavn>-<concept name>` (v8/v9) |
| VT-ID-DUPLICATE | error | row key unique (v7; in v8/v9 see VT-URI-DUPLICATE) |
| VT-KORTNAVN | error | kortnavn: letters, digits and hyphens, starting with a letter or digit (e.g. `N101`, `crochet-us`) |
| VT-URI-MISSING / VT-URI-FORMAT / VT-URI-DUPLICATE | error | concept name in column B present, CamelCase letters and digits, unique (S03) |
| VT-URI-LABEL | info | concept name differs from the CamelCase form of the main-language term |
| VT-REQ-LABEL / VT-REQ-DEF | error | prefLabel and definition present in the main language (`hovedspråk`, default nb) |
| VT-REQ-DEF-CODE | warning | code entry (has `skos:notation`) without a definition: code-table entries often have none in the source |
| VT-DEF-DERIVED | info | definition derived from the code table (`[avledet]`), not quoted from the source; check it |
| VT-REF-FORMAT | error | relation values are concept names (v8/v9) |
| VT-PREFIX | error | no `vok:` prefix in the cells of the Excel table (relations, `dct:subject`, notes); use the concept name |
| VT-PREFIX-KODE | info | `kode:` references to code lists; kept until the handling of code lists is decided |
| VT-REF-SELF | error | no relation to itself |
| VT-CYCLE-BROADER / VT-CYCLE-PARTOF | error | no cycles |
| VT-RELATED-CLASH | error | `related` not combined with a broader/narrower path (SKOS integrity) |
| VT-REF-DANGLING | warning | relation target exists in the workbook |
| VT-TYPE1-ISOLATED | warning | type 1 concept has at least one link |
| VT-TYPE1-BROADER-NON-TYPE1 | warning | broader of a type 1 concept is type 1 (OWL rule O4) |
| VT-LABEL-DUPLICATE | warning | main-language prefLabel unique |
| VT-LABEL-HOMONYM | warning | same term (any label or abbreviation, any language) on different concepts, e.g. US/UK *double crochet* |
| VT-LABEL-NOTED | info | a label clash (homonym, variant or duplicate) that the concept's scope note documents by naming the other concept's ID |
| VT-LABEL-VARIANT | info | same term means different concepts in two regional variants (en-US vs en-GB); this is the difference the vocabulary documents |
| VT-LABEL-CASE | warning | main-language prefLabel lowercase, except acronyms (S05) |
| VT-LABEL-GROUPING | warning | heuristic: label lists several items ("… og …") and has ≥2 narrower concepts, so it is probably a table heading |
| VT-SOURCE-REL | warning | `skosno:relationshipWithSource` is `self-composed`, `derived-from-source` or `direct-from-source`; spaces instead of hyphens and the template's Norwegian labels (`egendefinert`/`eigendefinert`, `basert på kilde`/`basert på kjelde`, `sitat fra kilde`/`sitat frå kjelde`) are accepted |
| VT-AUDIENCE | warning | `dct:audience` is `allmennheten`/`public` or `spesialist`/`specialist`; the RDF uses the data.norge.no audience-type URIs |
| VT-STATUS / VT-STATUS-LITERAL | warning | status is one of kandidat, gjeldende, utdatert, forkastet, written as a plain value |
| VT-TYPE-INVALID | warning | type is 1, 2 or 3 |
| VT-CONTACT | warning | contactPoint present |
| VT-COLL-SINGLE | warning | a collection has only one member (often a misspelt name) |
| VT-COLL-SIMILAR | warning | two collection names are almost the same (`Vegnettstilknytning` / `Vegnetstilknytning`) |
| VT-COLL-SPELLING | warning | one collection is written in more than one way (`Hoveddata` / `hoveddata`); the first spelling becomes the label |
| VT-COLL-SYNTAX | warning | the main-language scope note mentions a collection, but not in the fixed sentence |
| VT-COLL-OTHER-LANG | warning | a collection sentence in a scope note in another language; only the main-language note is read |
| VT-COLL-MEMBERS | info | each collection with its members |
| VT-COLL-FORM | info | `samlingen` used with several names, or `samlingene` with one |
| VT-COLL-CONCEPT | info | a collection has the same name as a concept; if that row is only a heading, set its status to `forkastet` |
| VT-TYPE-EMPTY / VT-NN-MISSING | info | expected gaps (source concepts; nn left for the expert, only when the main language is nb) |

The rule texts in the code are in `RULES` in `vocabtool/validate.py` (see [`docs/api/validate.md`](docs/api/validate.md)).

## Graph page

The graph page is a single HTML file and loads no JavaScript libraries. Google Fonts are optional and fall back to
system fonts when offline. In the page you can filter by relation type and concept type, search by label or concept
name, show a concept's 1–3 step neighbourhood, and mark validation findings. The side panel lists all relations,
including inverse ones (narrower, has part) and targets that are missing from the workbook. With several label
languages, a selector switches the node labels (e.g. en-US / en-GB), and the side panel shows all labels, definitions
and scope notes.

## Documentation and tests

- **API reference:** [`docs/api/`](docs/api/README.md) has one Markdown page per module, with the constants, classes
  and functions and their docstrings. GitHub renders the pages as they are, and they can be exported from there (or
  converted with pandoc, e.g. `pandoc docs/api/*.md -o vocabtool-api.docx`). Regenerate them after changing the code:

  ```bash
  python tools/gen_api_docs.py
  ```

  The generator uses only the Python standard library and reads the code without importing it.
- **Docstrings** follow the Google style: a summary line, a blank line, more text, and the sections `Args:`,
  `Returns:`, `Raises:` and `Attributes:` with indented `name: text` entries. Every module, class and function has one;
  a comment directly above a constant (or at the end of its line) becomes its description in the reference.
- **Tests:**

  ```bash
  .venv/bin/python tests/test_lists.py
  .venv/bin/python tests/test_type.py
  ```

- **GitHub workflow** (`.github/workflows/docs.yml`): on every push and pull request, checks that `docs/api/` matches
  the code (`python tools/gen_api_docs.py --check`) and runs the tests.

## Layout

```
vocabtool/__init__.py        package overview
vocabtool/cli.py             command line (python -m vocabtool <command>)
vocabtool/reader.py          read v7/v8/v9 workbooks into records
vocabtool/validate.py        the VT rules
vocabtool/graph.py           graph data + page (graph_template.html)
vocabtool/linkml_rdf.py      Excel -> LinkML data -> RDF, SHACL fixes and validation
vocabtool/migrate.py         v7 -> v9
vocabtool/template_ext.py    formulas, Excel table, header colours, language columns
vocabtool/lists.py           value lists and dropdowns (sheet lister), written on every save
vocabtool/uri.py             concept names (CamelCase), the column B formula, URIs
vocabtool/rename.py          rename a concept and its references, or a collection
vocabtool/samling.py         collections from the scope-note sentence
vocabtool/clash_notes.py     draft scope notes for label clashes
vocabtool/owl_import.py      OWL classes -> concepts, merging with existing ones
vocabtool/extract.py         extraction from text: chapters, prompts, record checks, new rows
vocabtool/set_fields.py      write reviewed values into concepts by name
schema/                      LinkML schema, generated artefacts, cross-row SHACL
templates/                   empty templates: v9 (master), v9 with language extension, v7
docs/status.md               project status and decisions
docs/api/                    API reference, generated from the docstrings
tools/gen_api_docs.py        generator of docs/api/
tests/                       tests (value lists, type column)
.github/workflows/docs.yml   API reference check and tests on GitHub
datasets/hekling/            example dataset: crochet stitches and patterns (en-US main; nb, en-GB, de, es)
datasets/hekling/out/        its check report, graph, YAML and Turtle
samples/                     your workbooks (not in git)
out/                         generated output (not in git)
```

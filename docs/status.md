# Project status

As of 10 November 2026. This is a summary of the work so far, for picking up the work in a new session.
The crochet example (`datasets/hekling/`) is described in its own README.

## Repository

- Public: <https://github.com/UteBroenner/skos-from-pdf-via-excel>.
- Contents:
  - `vocabtool/`: Python tools
  - `schema/`: LinkML schema, generated artefacts and cross-row SHACL
  - `templates/`: empty templates for v8 (master), v8 with language extension, and v7
  - `datasets/hekling/`: example vocabulary
- **Not in the repository:** Statens vegvesen vocabularies (N101, V440, BRUTUS) and their outputs. They are kept in
  `samples/` and `out/`, which are ignored by git, and were removed from the history. Upload them to a session when they are needed.

## Template v8: decisions in force

- **Master:** `templates/SKOS-Excel-mal-v8-for-import.xlsx` (the owner's layout).
  - Scheme rows: B14 `kortnavn`, B15 title, B16 `dct:creator`, B17 publisher, B18 issued.
  - Requirement row 20, description row 21 (with merged cells), property row 23.
  - Technical names in row 24 (the header of the Excel table `begrepsliste`); data from row 25.
- **Column B (concept name) is the key.**
  - CamelCase from the main-language term (æ → ae, ø → o, å → aa; acronyms stay in capitals). No language suffix.
  - URI = ConceptScheme URI (B1, `…/vokabular/<kortnavn>`) + `/` + name, e.g. `…/vokabular/N101/Rekkverk`.
  - Relations (`skos:broader`, `xkos:isPartOf`, `skos:related`) are written as concept names, comma-separated.
- **Formula columns:**
  - column A `dct:identifier` = `<kortnavn>-<name>`
  - `endringshash` = `TEXTJOIN` of the row content without ID, dates and persons
  - AD `opprettet_av` = B16 (hidden)
- **`tier`** is the last column, outside the table. It is internal and not imported.
- **The table covers all rows and columns in use.** Power Automate reads only the table.
- **`kortnavn`:** letters, digits and hyphens, any length (e.g. `N101`, `crochet-us`).
- **Language extension** (optional template): a `hovedspråk` row (main language; default nb) and label, abbreviation,
  definition and scope-note columns per language. The checks follow the main language.
- **Label clashes** (the same term for different concepts) are documented in a scope note that names the other concept.
  The checker then reports them as info.
- **Concepts are not deleted.** Set the status to `forkastet` instead. Exception: rows in a draft that has
  never been imported may be deleted (e.g. section headings that became collections).
- **Collections** are recorded only in the main-language scope note: "Inngår i samlingen X." /
  "Inngår i samlingene X, Y." The tools build `skos:Collection` (URI `…/<kortnavn>/samling/<Name>`) and `skos:member`.
  There is no collection sheet, so nothing can diverge. `dct:subject` is for subject areas only.
  - The sentence is Norwegian only, whatever the main language. Collections are unordered and not nested.
  - Name as written = `skos:prefLabel` of the collection; names are separated by commas, not "og".
  - The checker reports one-member collections, near-identical names, unreadable sentences and the sentence
    in another language's scope note (`VT-COLL-*`). The graph page shows collections as squares.
- **Prefixes:** none in the Excel table (relations, `dct:subject`, notes): write `Rekkverk`, not `vok:Rekkverk`
  (`VT-PREFIX`, error). The hidden PREFIX rows of the template stay, and the machine-readable artefacts
  (LinkML schema and data, Turtle) keep their prefixes. `kode:` references stay until code lists are decided
  (`VT-PREFIX-KODE`, info).
- **Merging with another vocabulary** (decided for BRUTUS and V440): the vocabulary stays its own. Exact matches get
  `skos:exactMatch` to the other concept's URI, its definition copied, `dct:source` = that URI,
  `skosno:relationshipWithSource` = `direct-from-source` (value still to be confirmed against SKOS-AP-NO) and an editorial
  note "[kilde] Definisjon kopiert fra V440 (<name>)." Close matches get `skos:closeMatch` only, with no definition copied.
- **Duplicates and generic names:** keep one row per concept; a concept in several groups names all of them in the
  collection sentence. Generic names get a qualifier in V440 style: "<term>, <group>".

## Tools

Run as `python -m vocabtool <command>`. Details in the README.

| Command | Purpose |
| --- | --- |
| `check` | VT rules, report (`.md`, `.json`) and interactive graph page (with collections) |
| `migrate` | v7 → v8; keeps the v7 names, relations become names. Only for real v7 files: workbooks are kept in v8 format, and `migrate` is not extended for mixed layouts |
| `uri` | fills missing concept names |
| `rename` | renames a concept and every relation and note that refers to it; `--collection` renames a collection |
| `fit` | stretches the table, formatting and validation; writes the formulas |
| `rdf` | LinkML data, SKOS Turtle (with `skos:Collection`), LinkML and SHACL validation |
| `owl-import` | adds OWL classes as concepts, merging with existing ones (label, or a reviewed merge map) |

LinkML 1.12.1 has gaps that are worked around in project code: language tags, enum URIs, and three SHACL defects.
Cross-row rules are hand-written SHACL-SPARQL. See `schema/README.md`.

## Power Automate import (designed, not built)

1. Trigger: the workbook is saved in the SharePoint library. The file's *Modified By* is the editor.
2. Match each table row to its List item by `intern_identifikator`:
   - **new:** create the item
   - **`endringshash` differs:** update it and set `dato_sist_endret` and `sist_endret_av`
   - **equal:** skip
3. Store `endringshash` in a multi-line text column.
4. Use one reviewer per file at a time.

## Vocabularies

| | N101 | V440 | BRUTUS |
| --- | --- | --- | --- |
| Concepts | 283 | 329 (12 domains) | 79 in 9 collections |
| Code lists | not processed | 152 collections, 1,358 codes; not processed | n/a |
| Errors | 3 (related/broader clash) | 12 (domain/source concepts with invalid names) | 48 (definition missing) |
| Warnings | 19 references to concepts outside the workbook, 39 unlinked Tier 1 | 103, incl. 89 unlinked Tier 1, 6 table headings used as concepts, 6 homonyms | 2 (one-member collection; capital letter in the scheme row label) |
| Other | n/a | `vok:` removed from `dct:subject` and notes; `dct:subject` still points to the old v7 names; 109 notes with `kode:`; the source is mainly a coding manual | see `out/brutus-status.md` |

V440 next steps: rename the domain concepts and fix `dct:subject`; decide how to handle the table headings and homonyms;
extract the code lists from the PDF tables by script.

BRUTUS (Confluence field list, `kortnavn` `brutus`) is migrated to v8 and merged with V440. Details, open points
and the links to the graph pages are in `out/brutus-status.md` (local, not in git).

## Instructions (not yet in the repository)

The v7 instruction files were reviewed against v8: project instructions, `SKOS-felt-instruksjer-v7` and
`RDF-Turtle-felt-konverteringsregler-v7`. The prompt template v4.7 is missing.

The main changes needed:
- **Naming and relations (S00/S01/S03/S04, S10/V03):** concept name in B as key, relations by name, column A as formula.
- **Main language (S05/S06):** both rules follow `hovedspråk`.
- **Status (S21):** plain `kandidat`.
- **Change notes (S20/V13/G09):** use `adms:versionNotes`; there is no `skos:changeNote` column.
- **Validation tables:** replace most V rules with references to the VT rules.
- **Conversion rules:** reduce to the decisions the script implements.
- **Still to implement:** `dct:publisher` and `dct:issued` defaults.

**Open decisions:**
- S16: move `exactMatch`/`closeMatch` text to `editorialNote`?
- S18: `dct:subject` as a concept name?
- Code lists: shared scheme (K2/V19) or none (O3)? Each code list can now be a collection.
  Until then, `kode:` references in the Excel table stay (reported as info, `VT-PREFIX-KODE`); `vok:` is not used in the table.
- OWL import (V440, V441): broader conflicts between the OWL hierarchy and the workbook (kept as in the workbook);
  tiers for imported classes; definitions for the imported concepts (from the handbooks).
- May the instructions be public?
- `skosno:relationshipWithSource` value for copied definitions: is `direct-from-source` the right SKOS-AP-NO term?
- JSON-LD output (prefixes in its `@context`, generated by LinkML): wanted?
- The crochet example is not developed further for now.

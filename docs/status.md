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
- **Not in the repository:** Statens vegvesen vocabularies (N101, V440, V441, BRUTUS), their ontologies, the handbook
  texts and all outputs. They are kept in
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
- **Definitions of code entries** (concepts with `skos:notation`): a missing definition is a warning (`VT-REQ-DEF-CODE`),
  not an error, also in SHACL. `owl-import --derive-code-definitions` builds one from the code table, marked `[avledet]`
  (`VT-DEF-DERIVED`, info), to be replaced by a definition from the handbook where it has one.
- **Code-list containers** (classes under "Kodeliste" without a definition) get a derived definition
  ("kodeliste for … i V440 (v440-owl, kapittel …)", `[avledet]`). Chapter numbers in derived definitions are the
  ontology's own (V-5 …), not the handbook's.
- **Modelling classes** of the ontologies (e.g. byggverk, komponent, lokasjon) stay without a definition for the expert,
  flagged `[fagekspert]` in the editorial note.
- **Definitions from handbooks** are close paraphrases marked `[omskrivning] Definisjon fra <handbook> <chapter>.`
  with `relationshipWithSource` `derived-from-source`; a verbatim quote is marked `[kilde] Definisjon sitert fra …`
  with `direct-from-source`. They are kept in JSON files and applied with `set-fields` after `owl-import`.
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
| `set-fields` | writes reviewed values (e.g. definitions from a handbook) into concepts by name, from JSON |

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

| | N101 | V440 (with OWL import) | V441 (new) | BRUTUS |
| --- | --- | --- | --- | --- |
| Concepts | 283 | 948 (329 before; 148 OWL classes merged, 619 added) | 158, all from the V441 ontology | 79 in 9 collections |
| Code lists | not processed | 152 collections, 1,358 codes; code values not imported | code values not imported | n/a |
| Errors | 3 (related/broader clash) | 39: 27 modelling classes without a definition, 12 domain/source concepts with invalid names | 5 modelling classes without a definition | 28 (definition missing) |
| Definitions | n/a | 8 added from the handbook text, 584 derived from the code tables | 101 from the N-V441 text, 7 copied from V440, 52 derived | 20 added from V440 chapter 6 and N-V441 |
| Other | n/a | 52 concepts with two broader concepts (workbook and OWL), flagged `[fagekspert]`; `vok:` removed; 109 notes with `kode:` | linked to V440 by `exactMatch` | see `out/brutus-status.md` |

V440 next steps: rename the domain concepts and fix `dct:subject`; decide how to handle the table headings and homonyms;
extract the code lists from the PDF tables by script.

BRUTUS (Confluence field list, `kortnavn` `brutus`) is migrated to v8 and merged with V440 and V441. Details, open points
and the links to the graph pages are in `out/brutus-status.md` (local, not in git).

## Work of 10 November 2026 (summary)

- **Decisions:** collections in the scope-note sentence; no prefixes in the Excel table (`kode:` kept for now); merging
  vocabularies by `exactMatch` plus copied definition, `closeMatch` for near matches; one row per concept, generic names
  qualified; both broader concepts kept where the OWL hierarchy differs; code entries and code lists may have derived
  definitions; modelling classes stay with the expert; workbooks stay in v8 format. Details under *Template v8: decisions in force*.
- **Tools** (pull request #1, merged): `owl-import`, `set-fields`, collections in `check`, `rdf`, `rename` and the graph page,
  `VT-PREFIX`, `VT-PREFIX-KODE`, `VT-REQ-DEF-CODE`, `VT-DEF-DERIVED`; fixes in `fit` and `migrate`.
- **Vocabularies** (local): BRUTUS migrated, merged and cleaned up; the two V440 ontologies imported into V440; V441 built
  from its ontology; definitions taken from the handbook texts (V440, N-V441, with N400, N401 and R411 checked).
  The reviewed values are kept as JSON in `out/` and applied with `set-fields`; `out/rebuild-V440-V441.sh` rebuilds
  V440 and V441 from the sources in the right order.

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
- OWL import (V440, V441): the expert decides the 52 concepts with two broader concepts (flagged "[fagekspert]")
  and defines the modelling classes; tiers for the imported classes.
- BRUTUS size fields: a general concept with the V440 variants as narrower concepts, or split the field?
  Fields that none of the texts describe are listed in `out/brutus-status.md`.
- Graphs: the published V440 graph predates the OWL import; V441 has no graph yet.
- May the instructions be public?
- `skosno:relationshipWithSource` values: are `direct-from-source` (copied or quoted) and `derived-from-source`
  (paraphrased or derived) the right SKOS-AP-NO terms?
- JSON-LD output (prefixes in its `@context`, generated by LinkML): wanted?
- The crochet example is not developed further for now.

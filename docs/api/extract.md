# `vocabtool.extract`

Source: [`vocabtool/extract.py`](../../vocabtool/extract.py)

Extraction of concepts from text (TXT converted from PDF), one LLM agent per chapter.

```text
    prepare  TXT -> chapters or sections (one file each) + one prompt per chunk + manifest.json
    (run)    an agent per chapter reads its prompt and writes <chapter id>.json (records, see RECORD_FIELDS)
    collect  records -> schema check, quote check -> new rows in a v9 workbook + report
```

The content rules come from a field-instruction file given at prepare time, so no project-specific
rules live in this module. The agents only do judgement work; names, formulas, fixed fields,
flags and the source relationship are written by code.

## Constants

| Name | Meaning |
| --- | --- |
| `HEADING_RE` | Numbered headings, with or without a space after the number: "5Tiltak", "5 Tiltak", "2.5.3Hovedinspeksjon". Appendices: "<word> B" on a line of its own, with sections "B.3", "B.3.1Armering…". A line that ends in a page number is a table-of-contents entry, not a heading. |
| `APPENDIX_SECTION_RE` | appendix section heading: letter and number (A.1, B.2.3) |
| `TOC_ENTRY_RE` | a page number at the end of a line (table of contents entry) |
| `APPENDIX_WORDS` | words that start an appendix heading (default of --appendix-words) |
| `RECORD_FIELDS` | the fields of one agent record and what each must hold (also shown to the agent in the prompt) |
| `PROMPT` | prompt template for one chunk; placeholders are filled by prepare (--prompt-template replaces it) |

## Functions

### `split_text`

```python
def split_text(path, level: int=1, appendix_words=APPENDIX_WORDS, start_line: int | None=None, min_chars: int=0) -> list[dict]
```

Split a text into chunks at headings of depth <= level (1 = chapters, 2 = sections such as 5.2).

Headings are accepted only in order: a chapter must follow the previous one (5 after 4), a section must lie
inside the current chapter and come after the previous section. When chapter 1 (or appendix A) appears again before chapter 2 (or B),
everything before it is dropped, which removes front matter such as a foreword or the table of contents.
Numbered lines inside tables ("4 Aluminium" after chapter 7) are out of order and therefore ignored.
start_line (1-based) skips everything before it. Chunks shorter than min_chars are merged into the next chunk
of the same chapter.

### `prepare`

```python
def prepare(txt, out_dir, instructions, kortnavn, title_doc, known_workbooks=(), only=None, level=1, appendix_words=APPENDIX_WORDS, start_line=None, min_chars=0, prompt_template=None) -> list[dict]
```

prompt_template: a file with the same {placeholders} as PROMPT (title_doc, kortnavn, number, title, text,
known, instructions, fields, result_path); by default the built-in Norwegian prompt.

### `check_record`

```python
def check_record(r: dict) -> list[str]
```

Check one agent record against RECORD_FIELDS.

Records written with the former field name tier are accepted (renamed to type).

**Returns**

The problems found; an empty list means the record is valid.

### `lower_first`

```python
def lower_first(t: str) -> str
```

First letter lower case, unless the term starts with an acronym (G/S areal, ROS-analyse, NIB-bjelke).

### `collect`

```python
def collect(manifest_path, workbook, out, source, contact=None, kortnavn=None, title=None, link_workbooks=()) -> dict
```

Check the agents' records and add new concepts to the workbook.

- A record is rejected if it does not match the record format or its quote is not in the chunk.
- A term already in the workbook is not added again. If that concept has no definition and the record has
  one, the definition is written to <out>.suggestions.json (set-fields format) for review instead.
- A term that appears twice in the run is added once; the repeat is reported.
- link_workbooks: other v9 vocabularies. A new term that matches exactly one concept there gets
  skos:exactMatch to it and, if that concept has a definition from a source (not derived), its definition is
  copied with that concept as dct:source (merge rule). Relation targets found only there are reported.

### `report_md`

```python
def report_md(report: dict) -> str
```

Markdown report of extract collect: chapters, accepted, rejected, downgraded quotes, existing, links.

## Internal helpers

Documented in the source: `_depth`, `_num_key`, `_norm`, `_key`.

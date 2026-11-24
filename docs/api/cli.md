# `vocabtool.cli`

Source: [`vocabtool/cli.py`](../../vocabtool/cli.py)

Command line: python -m vocabtool <command> ...

```text
check    <workbook.xlsx> [--out DIR]          validate; writes report (.md + .json) and graph (.html)
migrate  <v7.xlsx> --template <v9.xlsx> --out <file.xlsx> [--kortnavn N101]
rdf      <v9.xlsx> [--out DIR]          LinkML route: data (.yaml), RDF (.ttl), LinkML + SHACL report (.md)
uri      <v9.xlsx> [--overwrite]        fill empty concept names (column B) from the main-language term
rename   <v9.xlsx> OLD NEW [OLD NEW …]  rename concepts (column B) and update relations and notes
         --collection OLD NEW            rename a collection in the scope-note sentences ("Inngår i samlingen …")
fit      <v9.xlsx>                      stretch the Excel table, formatting and validation to all rows and columns;
                                        write the formulas (A, B, opprettet_av, endringshash), the value lists and the dropdowns
owl-import <v9.xlsx> <owl.ttl> [...] --out <file.xlsx> [--link V440.xlsx] [--merge-map map.json]
           [--log log.json] [--contact E-MAIL] [--kortnavn V441 --title "…"] [--keep-root]
           [--derive-code-definitions] [--type 1]
                                        add OWL classes as concepts, merging with existing ones
extract prepare <text.txt> --out DIR --instructions FILE --kortnavn K --title T [--known v9.xlsx …] [--only ch5 …]
                [--level 2] [--min-chars N] [--appendix-words W,…] [--start-line N] [--prompt-template FILE]
                                        split the text into chapters and write one prompt per chapter (manifest.json)
extract collect <DIR>/manifest.json <v9.xlsx> --out <file.xlsx> --source URL [--contact E-MAIL] [--link v9.xlsx …]
                                        check the agents' JSON records (schema, quotes) and add the concepts
set-fields <v9.xlsx> <values.json> [--out <file.xlsx>]
                                        write reviewed values (e.g. definitions) into concepts by name
```

## Functions

### `report_md`

```python
def report_md(v, findings, summary) -> str
```

Markdown report of a check: summary per rule, then every error and warning.

**Args**

- `v`: the vocabulary that was checked.
- `findings`: all findings from validate.validate.
- `summary`: the result of validate.summarise(findings).

**Returns**

The report as Markdown text.

### `cmd_check`

```python
def cmd_check(a)
```

`check`: run the VT rules; write <stem>-report.md, -report.json and -graph.html to --out.

Returns 1 if there are errors, else 0.

### `cmd_migrate`

```python
def cmd_migrate(a)
```

`migrate`: copy a v7 workbook into the v9 template; also writes <out>.namemap.json (v7 URI -> name).

### `cmd_rdf`

```python
def cmd_rdf(a)
```

`rdf`: workbook -> LinkML data (.yaml) and Turtle (.ttl); LinkML and SHACL validation (-shacl-report.md).

Returns 1 if SHACL does not conform, else 0.

### `cmd_uri`

```python
def cmd_uri(a)
```

`uri`: write concept names into empty cells of column B (--overwrite: all), from the main-language term.

### `cmd_fit`

```python
def cmd_fit(a)
```

`fit`: write the formulas, stretch the Excel table and write the value lists and dropdowns.

### `cmd_rename`

```python
def cmd_rename(a)
```

`rename`: rename concepts (pairs OLD NEW) or, with --collection, one collection.

### `cmd_owl_import`

```python
def cmd_owl_import(a)
```

`owl-import`: add the classes of OWL files as concepts; writes a JSON log of merges and conflicts.

### `cmd_extract`

```python
def cmd_extract(a)
```

`extract prepare` (split the text, write prompts) or `extract collect` (check records, add concepts).

### `cmd_set_fields`

```python
def cmd_set_fields(a)
```

`set-fields`: write reviewed values from a JSON file into concepts, by concept name.

### `main`

```python
def main(argv=None)
```

Parse the command line and run the command.

**Args**

- `argv`: arguments without the program name; None reads sys.argv.

**Returns**

The exit code of the command (0 = success).

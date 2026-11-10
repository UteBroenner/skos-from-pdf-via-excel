# Templates

All three are empty: no concepts and no code lists. The remaining help texts ("for eksempel N101") are examples.

| File | Version | Use |
| --- | --- | --- |
| `SKOS-Excel-mal-v8-for-import.xlsx` | v8 (master) | Current template. One sheet `vokabular` with the Excel table `begrepsliste` (header row 24, data from row 25). Column B holds the concept name (key, CamelCase). Column A (`<kortnavn>-<name>`), `endringshash` and AD (`opprettet_av` = B16) are formulas. `tier` is the last column, outside the table. Hidden sheet `kodeverk` for code lists. |
| `SKOS-Excel-mal-v8-lang-ext.xlsx` | v8 + language extension | The master plus a `hovedspråk` row (B19) and columns for en-US, en-GB, de and es labels and abbreviations, an en-US definition and an en-US scope note. Created with `vocabtool/template_ext.py`. |
| `SKOS-Excel-mal-v7.xlsx` | v7 (previous) | For reference and for testing `vocabtool migrate`. Rebuilt from the v7 layout: one sheet `<kortnavn>-vokabular` with the URI `vok:<Name>` in column A and relations as `vok:<Name>`, a `kodeverk` sheet, and the mapping table from step 1c (`mapping-oppsummering`). |

Fill in the short name (`kortnavn`, letters, digits and hyphens, e.g. `N101`), the title and `dct:creator` first.
`python -m vocabtool fit <file>` stretches the table and the formulas to all rows you use.

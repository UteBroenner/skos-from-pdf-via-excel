"""Command line: python -m vocabtool <command> ...

  check    <workbook.xlsx> [--out DIR]          validate; writes report (.md + .json) and graph (.html)
  migrate  <v7.xlsx> --template <v8.xlsx> --out <file.xlsx> [--kortnavn N101]
  rdf      <v8.xlsx> [--out DIR]          LinkML route: data (.yaml), RDF (.ttl), LinkML + SHACL report (.md)
  uri      <v8.xlsx> [--overwrite]        fill empty concept names (column B) from the main-language term
  fit      <v8.xlsx>                      stretch the Excel table, formatting and validation to all rows and columns
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .reader import read_workbook
from .validate import validate, summarise
from .graph import write_graph
from .migrate import migrate


def report_md(v, findings, summary) -> str:
    lines = [f"# Validation report: {v.path.name}", "",
             f"Template {v.version} · kortnavn `{v.kortnavn}` · {len(v.concepts)} concepts "
             f"(code lists not checked)", "",
             f"**{summary['errors']} errors, {summary['warnings']} warnings, {summary['info']} info**", "",
             "| Severity | Rule | Count | Meaning |", "| --- | --- | ---: | --- |"]
    lines += [f"| {r['severity']} | {r['rule']} | {r['count']} | {r['description']} |" for r in summary["by_rule"]]
    lines += ["", "## Findings (errors and warnings)", "", "| Severity | Rule | ID | Tab | Row | Detail |",
              "| --- | --- | --- | --- | ---: | --- |"]
    order = {"error": 0, "warning": 1}
    for f in sorted((f for f in findings if f.severity != "info"), key=lambda f: (order[f.severity], f.rule, f.sheet or "", f.row or 0)):
        lines.append(f"| {f.severity} | {f.rule} | {f.key or ''} | {f.sheet or ''} | {f.row or ''} | {f.message.replace('|', '/')} |")
    return "\n".join(lines) + "\n"


def cmd_check(a):
    v = read_workbook(a.workbook)
    findings = validate(v)
    summary = summarise(findings)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stem = Path(a.workbook).stem
    (out / f"{stem}-report.md").write_text(report_md(v, findings, summary), encoding="utf-8")
    (out / f"{stem}-report.json").write_text(json.dumps(
        {"file": v.path.name, "version": v.version, "kortnavn": v.kortnavn, "concepts": len(v.concepts),
         "summary": summary, "findings": [f.as_dict() for f in findings]}, ensure_ascii=False, indent=1), encoding="utf-8")
    g = write_graph(v, findings, out / f"{stem}-graph.html")
    print(f"{v.path.name}: {len(v.concepts)} concepts, {summary['errors']} errors, {summary['warnings']} warnings")
    for r in summary["by_rule"]:
        print(f"  {r['severity']:<8}{r['rule']:<24}{r['count']:>5}  {r['description']}")
    print(f"report: {out / (stem + '-report.md')}\ngraph:  {g}")
    return 1 if summary["errors"] else 0


def cmd_migrate(a):
    r = migrate(a.workbook, a.template, a.out, kortnavn=a.kortnavn)
    print(f"{r['concepts']} concepts -> {r['target']} (rows {r['rows']}, kortnavn {r['kortnavn']})")
    if r["unresolved_relations"]:
        print(f"{len(r['unresolved_relations'])} relation targets not in the workbook, kept as written:")
        for i, f, t in r["unresolved_relations"]:
            print(f"  {i} {f} -> {t}")
    if r["fields_without_v8_column"]:
        print("fields with no v8 column (not migrated):", ", ".join(r["fields_without_v8_column"]))
    if r["change_note_moved_to_version_notes"]:
        print(f"{r['change_note_moved_to_version_notes']} skos:changeNote values moved to adms:versionNotes")
    map_path = Path(a.out).with_suffix(".idmap.json")
    map_path.write_text(json.dumps(r["id_map"], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ID map: {map_path}")
    return 0


def cmd_rdf(a):
    import logging
    from collections import Counter
    logging.disable(logging.WARNING)
    from linkml.validator import validate as linkml_validate
    from .linkml_rdf import (schemaview, workbook_to_data, data_to_graph, build_shapes, shacl_validate,
                             write_yaml, SCHEMA, ROOT)
    sv = schemaview()
    v = read_workbook(a.workbook)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stem = Path(a.workbook).stem
    data = workbook_to_data(v, sv)
    write_yaml(data, out / f"{stem}.yaml")
    lres = linkml_validate(data, str(SCHEMA), "ConceptScheme").results
    skipped = []
    g = data_to_graph(data, sv, skipped)
    g.serialize(out / f"{stem}.ttl", format="turtle")
    shapes = build_shapes(ROOT / "schema" / "generated" / "svv_vokabular.shacl.ttl", sv)
    conforms, sres = shacl_validate(g, shapes)
    short = lambda u: u.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
    lines = [f"# LinkML / SHACL report: {v.path.name}", "",
             f"{len(data['concepts'])} concepts · {len(g)} triples · SHACL conforms: **{conforms}**", "",
             f"## LinkML validation ({len(lres)} issues)", ""]
    lines += [f"- {r.message}" for r in lres[:200]]
    lines += ["", f"## Values not written to RDF ({len(skipped)}, not IRIs)", "", "| Concept | Slot | Value |", "| --- | --- | --- |"]
    lines += [f"| {short(s_)} | {sl} | {val.replace('|', '/')} |" for s_, sl, val in skipped]
    lines += ["", f"## SHACL results ({len(sres)})", "", "| Severity | Concept | Path | Value | Message |", "| --- | --- | --- | --- | --- |"]
    for r in sorted(sres, key=lambda r: (r["severity"] != "Violation", r["focus"])):
        lines.append(f"| {r['severity']} | {short(r['focus'])} | {short(r['path'])} | {short(r['value'])} | {r['message'][:120].replace('|', '/')} |")
    (out / f"{stem}-shacl-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{v.path.name}: {len(data['concepts'])} concepts, {len(g)} triples")
    print(f"  LinkML validation: {len(lres)} issues")
    print(f"  not written to RDF (not IRIs): {len(skipped)}")
    c = Counter((r["severity"], r["message"].split(":")[0][:60] if r["message"].startswith("VT-") else r["component"].replace("ConstraintComponent", "") + " " + short(r["path"])) for r in sres)
    print(f"  SHACL conforms={conforms}, {len(sres)} results")
    for (sev, k), n in sorted(c.items()):
        print(f"    {sev:<10}{k:<45}{n:>5}")
    print(f"  files: {out / (stem + '.ttl')}, {out / (stem + '.yaml')}, {out / (stem + '-shacl-report.md')}")
    return 0 if conforms else 1


def cmd_uri(a):
    import openpyxl
    from .reader import normalise_header
    from .template_ext import uri_as_value, fit_table
    from .uri import assign_names, concept_uri
    v = read_workbook(a.workbook)
    names = assign_names(v.concepts, v.label_field, overwrite=a.overwrite, main_lang=v.main_lang)
    collisions = names.pop("_collisions")
    wb = openpyxl.load_workbook(a.workbook)
    uri_as_value(wb)
    ws = wb["vokabular"]
    by_key = v.by_key()
    for key, name in names.items():
        ws.cell(by_key[key].row, 2).value = name
    fit_table(wb)
    wb.save(a.workbook)
    print(f"{len(names)} concept names written to column B of {a.workbook}"
          + (f" (URI e.g. {concept_uri(v.scheme_uri, next(iter(names.values())))})" if names and v.scheme_uri else ""))
    for key, base, name in collisions:
        print(f"  {key}: '{base}' is taken, used '{name}'; choose a better name in column B")
    return 0


def cmd_fit(a):
    import openpyxl
    from .template_ext import fit_table
    wb = openpyxl.load_workbook(a.workbook)
    r = fit_table(wb)
    wb.save(a.workbook)
    print(f"{a.workbook}: {r}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="vocabtool")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("workbook"); c.add_argument("--out", default="out"); c.set_defaults(fn=cmd_check)
    m = sub.add_parser("migrate"); m.add_argument("workbook"); m.add_argument("--template", required=True)
    m.add_argument("--out", required=True); m.add_argument("--kortnavn"); m.set_defaults(fn=cmd_migrate)
    r = sub.add_parser("rdf"); r.add_argument("workbook"); r.add_argument("--out", default="out/rdf"); r.set_defaults(fn=cmd_rdf)
    u = sub.add_parser("uri"); u.add_argument("workbook"); u.add_argument("--overwrite", action="store_true"); u.set_defaults(fn=cmd_uri)
    ft = sub.add_parser("fit"); ft.add_argument("workbook"); ft.set_defaults(fn=cmd_fit)
    a = p.parse_args(argv)
    return a.fn(a)

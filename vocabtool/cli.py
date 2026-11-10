"""Command line: python -m vocabtool <command> ...

  check    <workbook.xlsx> [--out DIR]          validate; writes report (.md + .json) and graph (.html)
  migrate  <v7.xlsx> --template <v8.xlsx> --out <file.xlsx> [--kortnavn N101]
  rdf      <v8.xlsx> [--out DIR]          LinkML route: data (.yaml), RDF (.ttl), LinkML + SHACL report (.md)
  uri      <v8.xlsx> [--overwrite]        fill empty concept names (column B) from the main-language term
  rename   <v8.xlsx> OLD NEW [OLD NEW …]  rename concepts (column B) and update relations and notes
           --collection OLD NEW            rename a collection in the scope-note sentences ("Inngår i samlingen …")
  fit      <v8.xlsx>                      stretch the Excel table, formatting and validation to all rows and columns;
                                          write the formulas for column A and endringshash
  owl-import <v8.xlsx> <owl.ttl> [...] --out <file.xlsx> [--link V440.xlsx] [--merge-map map.json]
             [--log log.json] [--contact E-MAIL] [--kortnavn V441 --title "…"] [--keep-root]
             [--derive-code-definitions]
                                          add OWL classes as concepts, merging with existing ones
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
    map_path = Path(a.out).with_suffix(".namemap.json")
    map_path.write_text(json.dumps(r["name_map"], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"v7 URI -> v8 name map: {map_path}")
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
             f"{len(data['concepts'])} concepts · {len(data.get('collections', []))} collections · {len(g)} triples · SHACL conforms: **{conforms}**", "",
             f"## LinkML validation ({len(lres)} issues)", ""]
    lines += [f"- {r.message}" for r in lres[:200]]
    lines += ["", f"## Values not written to RDF ({len(skipped)}, not IRIs)", "", "| Concept | Slot | Value |", "| --- | --- | --- |"]
    lines += [f"| {short(s_)} | {sl} | {val.replace('|', '/')} |" for s_, sl, val in skipped]
    lines += ["", f"## SHACL results ({len(sres)})", "", "| Severity | Concept | Path | Value | Message |", "| --- | --- | --- | --- | --- |"]
    for r in sorted(sres, key=lambda r: (r["severity"] != "Violation", r["focus"])):
        lines.append(f"| {r['severity']} | {short(r['focus'])} | {short(r['path'])} | {short(r['value'])} | {r['message'][:120].replace('|', '/')} |")
    (out / f"{stem}-shacl-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{v.path.name}: {len(data['concepts'])} concepts, {len(data.get('collections', []))} collections, {len(g)} triples")
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
    from .template_ext import uri_as_value, fit_table, apply_formulas
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
    apply_formulas(wb)
    wb.save(a.workbook)
    print(f"{len(names)} concept names written to column B of {a.workbook}"
          + (f" (URI e.g. {concept_uri(v.scheme_uri, next(iter(names.values())))})" if names and v.scheme_uri else ""))
    for key, base, name in collisions:
        print(f"  {key}: '{base}' is taken, used '{name}'; choose a better name in column B")
    return 0


def cmd_fit(a):
    import openpyxl
    from .template_ext import fit_table, apply_formulas
    wb = openpyxl.load_workbook(a.workbook)
    r = fit_table(wb)
    apply_formulas(wb)
    wb.save(a.workbook)
    print(f"{a.workbook}: {r}")
    return 0


def cmd_rename(a):
    from .rename import rename, rename_collection
    if a.collection:
        if len(a.pairs) != 2:
            raise SystemExit("give one pair: --collection OLD NEW")
        r = rename_collection(a.workbook, *a.pairs)
        print(f"{a.workbook}: collection renamed in {r['notes']} scope notes")
        return 0
    if len(a.pairs) % 2:
        raise SystemExit("give pairs: OLD NEW [OLD NEW …]")
    pairs = dict(zip(a.pairs[::2], a.pairs[1::2]))
    r = rename(a.workbook, pairs)
    print(f"{a.workbook}: {r['names']} names, {r['relations']} relation values, {r['notes']} notes updated")
    return 0


def cmd_owl_import(a):
    import json
    from collections import Counter
    from .owl_import import owl_import
    log = owl_import(a.workbook, a.owl, a.out, link=a.link, merge_map=a.merge_map, contact=a.contact,
                     keep_root=a.keep_root, kortnavn=a.kortnavn, title=a.title,
                     derive_code_definitions=a.derive_code_definitions)
    log_path = Path(a.log or Path(a.out).with_suffix(".owl-import.json"))
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.out}: {len(log['merged'])} classes merged, {len(log['new'])} new concepts, "
          f"{len(log['linked'])} linked to {a.link or '-'}, {len(log['derived'])} code definitions derived, "
          f"{len(log['skipped'])} skipped")
    if log["conflicts"]:
        n = Counter(c["field"] for c in log["conflicts"])
        if n.get("broader"):
            print(f"  {n['broader']} concepts with a different OWL parent: both broader concepts kept, flagged [fagekspert]")
        if n.get("notation"):
            print(f"  {n['notation']} codes differ from the OWL kode: kept as in the workbook")
    print(f"  log: {log_path}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="vocabtool")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("workbook"); c.add_argument("--out", default="out"); c.set_defaults(fn=cmd_check)
    m = sub.add_parser("migrate"); m.add_argument("workbook"); m.add_argument("--template", required=True)
    m.add_argument("--out", required=True); m.add_argument("--kortnavn"); m.set_defaults(fn=cmd_migrate)
    r = sub.add_parser("rdf"); r.add_argument("workbook"); r.add_argument("--out", default="out/rdf"); r.set_defaults(fn=cmd_rdf)
    u = sub.add_parser("uri"); u.add_argument("workbook"); u.add_argument("--overwrite", action="store_true"); u.set_defaults(fn=cmd_uri)
    rn = sub.add_parser("rename"); rn.add_argument("workbook"); rn.add_argument("pairs", nargs="+")
    rn.add_argument("--collection", action="store_true", help="rename a collection, not a concept"); rn.set_defaults(fn=cmd_rename)
    ft = sub.add_parser("fit"); ft.add_argument("workbook"); ft.set_defaults(fn=cmd_fit)
    oi = sub.add_parser("owl-import", help="add OWL classes as concepts, merging with existing ones")
    oi.add_argument("workbook", help="v8 workbook (an empty template for a new vocabulary)")
    oi.add_argument("owl", nargs="+", help="OWL files (Turtle), imported in this order")
    oi.add_argument("--out", required=True, help="workbook to write")
    oi.add_argument("--link", help="other v8 workbook: copy definitions of exact label matches (merge rule)")
    oi.add_argument("--merge-map", help="JSON {class IRI: concept name} for reviewed merges of variant labels")
    oi.add_argument("--log", help="log file (default: <out>.owl-import.json)")
    oi.add_argument("--contact", help="dcat:contactPoint for new concepts")
    oi.add_argument("--kortnavn"); oi.add_argument("--title")
    oi.add_argument("--keep-root", action="store_true", help="import the single top class of a file too")
    oi.add_argument("--derive-code-definitions", action="store_true",
                    help="give new code entries a definition built from code and broader, marked [avledet]")
    oi.set_defaults(fn=cmd_owl_import)
    a = p.parse_args(argv)
    return a.fn(a)

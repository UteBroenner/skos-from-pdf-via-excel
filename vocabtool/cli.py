"""Command line: python -m vocabtool <command> ...

  check    <workbook.xlsx> [--out DIR]          validate; writes report (.md + .json) and graph (.html)
  migrate  <v7.xlsx> --template <v8.xlsx> --out <file.xlsx> [--kortnavn N101]
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


def main(argv=None):
    p = argparse.ArgumentParser(prog="vocabtool")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("workbook"); c.add_argument("--out", default="out"); c.set_defaults(fn=cmd_check)
    m = sub.add_parser("migrate"); m.add_argument("workbook"); m.add_argument("--template", required=True)
    m.add_argument("--out", required=True); m.add_argument("--kortnavn"); m.set_defaults(fn=cmd_migrate)
    a = p.parse_args(argv)
    return a.fn(a)

"""Build a self-contained interactive graph page (no external JS libraries)."""
from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

from .reader import Vocabulary, label_fields, split_multi
from .validate import Finding

TEMPLATE = Path(__file__).with_name("graph_template.html")
EDGE_TYPE = {"broader": "broader", "is_part_of": "isPartOf", "related": "related"}


def graph_data(v: Vocabulary, findings: list[Finding]) -> dict:
    by_key = v.by_key()
    issues: dict[str, list] = {}
    for f in findings:
        if f.key:
            issues.setdefault(f.key, []).append([f.severity, f.rule, f.message])
    nodes, edges, dangling, seen = [], [], [], set()
    langs_seen: dict[str, int] = {}
    for c in v.concepts:
        labels, alts, defs = {}, {}, {}
        for fld, val in c.fields.items():
            if fld.startswith("def_") and val:
                tag = fld[4:].split("_")
                defs["-".join([tag[0]] + [t.upper() for t in tag[1:]])] = val
        for fld, tag in label_fields(c.fields).items():
            if not c.get(fld):
                continue
            if fld.startswith("label_"):
                labels[tag] = c.get(fld)
            else:
                alts[tag] = ", ".join(split_multi(c.get(fld)))
        for tag in labels:
            langs_seen[tag] = langs_seen.get(tag, 0) + 1
        nodes.append({"id": c.key, "label": c.get(v.label_field) or c.key, "tier": c.tier or "",
                      "sheet": c.sheet, "def": c.get(v.def_field) or "", "defs": defs,
                      "alt": "; ".join(f"{v} ({t})" for t, v in alts.items()),
                      "labels": labels, "alts": alts,
                      "notes": [v for f, v in c.fields.items() if f.startswith("scope_note") and v], "issues": issues.get(c.key, [])})
        for fld, typ in EDGE_TYPE.items():
            for t in c.relations.get(fld, []):
                if t in by_key and t != c.key:
                    sig = (typ, *sorted((c.key, t))) if typ == "related" else (typ, c.key, t)
                    if sig in seen:      # related stated in both directions -> draw once
                        continue
                    seen.add(sig)
                    edges.append({"s": c.key, "t": t, "type": typ})
                elif t != c.key:
                    dangling.append({"s": c.key, "t": t, "type": typ})
    return {
        "meta": {"title": v.title, "kortnavn": v.kortnavn, "version": v.version, "file": v.path.name,
                 "generated": date.today().isoformat(),
                 "main_lang": v.main_lang,
                 "langs": sorted(langs_seen, key=lambda t: (t != v.main_lang, t != "nb", t != "nn", t))},
        "nodes": nodes, "edges": edges, "dangling": dangling,
    }


def write_graph(v: Vocabulary, findings: list[Finding], dst: str | Path, title: str | None = None) -> Path:
    data = graph_data(v, findings)
    page_title = title or f"{v.kortnavn or 'Vocabulary'} concept graph"
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out = TEMPLATE.read_text(encoding="utf-8")
    out = out.replace("__TITLE__", html.escape(page_title)).replace("/*__DATA__*/null", payload)
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    return dst

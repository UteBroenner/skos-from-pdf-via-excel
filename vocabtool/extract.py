"""Extraction of concepts from text (TXT converted from PDF), one LLM agent per chapter.

    prepare  TXT -> chapters (one file each) + one prompt per chapter + manifest.json
    (run)    an agent per chapter reads its prompt and writes <chapter id>.json (records, see RECORD_FIELDS)
    collect  records -> schema check, quote check -> new rows in a v8 workbook + report

The content rules come from a field-instruction file given at prepare time, so no project-specific
rules live in this module. The agents only do judgement work; names, formulas, fixed fields,
flags and the source relationship are written by code.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import openpyxl

from .reader import read_workbook, normalise_header
from .template_ext import fit_table, apply_formulas
from .uri import local_name

# ---------------------------------------------------------------- split
# Headings in PDF-to-text output: number glued to the title ("5Tiltak", "2.5.3Hovedinspeksjon", "B.3.1Armering…"),
# appendices as "Tillegg B" on a line of their own. Everything before the first "1<Title>" is front matter (TOC).
CHAPTER_RE = re.compile(r"^(?P<num>\d{1,2})(?P<title>[A-ZÆØÅ][^\n]*[a-zæøå][^\n]*)$")
APPENDIX_RE = re.compile(r"^Tillegg (?P<num>[A-Z])\s*$")


def split_text(path) -> list[dict]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    heads, started = [], False
    for i, line in enumerate(lines):
        s = line.strip()
        m = CHAPTER_RE.match(s)
        if m and len(m.group("title")) >= 4:
            if m.group("num") == "1":
                started = True
            if started:
                heads.append((i, m.group("num"), m.group("title").strip()))
            continue
        m = APPENDIX_RE.match(s)
        if m and started:
            nxt = next((l.strip() for l in lines[i + 1:i + 4] if l.strip()), "")
            heads.append((i, m.group("num"), nxt[:80]))
    chunks = []
    for k, (i, num, title) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        text = "\n".join(lines[i:end]).strip()
        cid = f"kap{num}" if num.isdigit() else f"tillegg{num}"
        chunks.append({"id": cid, "number": num, "title": title, "start_line": i + 1, "end_line": end,
                       "chars": len(text), "text": text})
    return chunks


# ---------------------------------------------------------------- prompt
RECORD_FIELDS = {
    "term": "anbefalt term på hovedspråket, med liten forbokstav unntatt akronymer",
    "section": "avsnittsnummeret der begrepet defineres eller innføres, f.eks. 5.2 eller B.3.1",
    "quote": "ordrett setning fra kapitlet som definerer eller innfører begrepet (kopier tegn for tegn)",
    "definition": "definisjon på hovedspråket, genus/differentia, liten forbokstav, uten punktum til slutt; tom hvis kilden ikke gir grunnlag",
    "definition_kind": "\"quote\" hvis definisjonen er ordrett fra kilden, \"paraphrase\" hvis omskrevet, \"none\" hvis tom",
    "tier": "1, 2 eller 3",
    "alt_labels": "liste med tillatte termer og akronymer fra kilden (kan være tom)",
    "notation": "kode fra kilden, ellers null",
    "broader": "liste med termer (ikke navn) for overbegreper, bare når kilden uttrykker det",
    "is_part_of": "liste med termer for helheter begrepet er del av, bare når kilden uttrykker det",
    "related": "liste med termer for relaterte begreper, bare når kilden kobler dem uttrykkelig",
    "cue": "ordene i kilden som begrunner relasjonene (f.eks. «omfatter», «består av»), ellers null",
    "uncertain": "kort beskrivelse av det du er usikker på (tier, relasjon, sammenslåing), ellers null",
}

PROMPT = """Du ekstraherer begreper fra ett kapittel av kilden «{title_doc}» (kortnavn {kortnavn}).
Les bare kapitlet under. Følg feltinstruksene under. Du skal KUN ekstrahere – ikke mappe, validere eller konvertere.

## Kapittel {number}: {title}

<kapittel>
{text}
</kapittel>

## Begreper som allerede finnes (ikke lag dem på nytt; bruk termen når du peker på dem i relasjoner)

{known}

## Feltinstrukser

{instructions}

## Svar

Svar med JSON og ingenting annet: en liste med ett objekt per begrep, med disse feltene:

{fields}

Regler for svaret:
- `quote` må stå ordrett i kapitlet; svar uten et slikt sitat blir forkastet.
- Ikke finn opp noe; heller færre begreper enn gjetning. Usikkerhet skrives i `uncertain`.
- Overskrifter som bare grupperer andre begreper er ikke begreper.
- Lagre svaret som {result_path}
"""


def prepare(txt, out_dir, instructions, kortnavn, title_doc, known_workbooks=(), only=None) -> list[dict]:
    out = Path(out_dir)
    (out / "chapters").mkdir(parents=True, exist_ok=True)
    (out / "prompts").mkdir(exist_ok=True)
    (out / "results").mkdir(exist_ok=True)
    rules = Path(instructions).read_text(encoding="utf-8")
    known = []
    for wb in known_workbooks:
        v = read_workbook(wb)
        known += [f"- {c.get(v.label_field)} ({v.kortnavn})" for c in v.concepts if c.get(v.label_field)]
    fields = "\n".join(f"- `{k}`: {d}" for k, d in RECORD_FIELDS.items())
    chunks = split_text(txt)
    manifest = []
    for ch in chunks:
        if only and ch["id"] not in only:
            continue
        (out / "chapters" / f"{ch['id']}.txt").write_text(ch["text"], encoding="utf-8")
        result = out / "results" / f"{ch['id']}.json"
        prompt = PROMPT.format(title_doc=title_doc, kortnavn=kortnavn, number=ch["number"], title=ch["title"],
                               text=ch["text"], known="\n".join(known) or "(ingen)", instructions=rules,
                               fields=fields, result_path=result)
        (out / "prompts" / f"{ch['id']}.md").write_text(prompt, encoding="utf-8")
        manifest.append({k: ch[k] for k in ("id", "number", "title", "start_line", "end_line", "chars")}
                        | {"prompt": str(out / "prompts" / f"{ch['id']}.md"), "result": str(result),
                           "prompt_chars": len(prompt), "done": result.exists()})
    (out / "manifest.json").write_text(json.dumps({"source": str(txt), "kortnavn": kortnavn, "title": title_doc,
                                                   "chapters": manifest}, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest


# ---------------------------------------------------------------- collect
def _norm(s: str) -> str:
    s = s.replace(" ", " ").replace("«", '"').replace("»", '"').replace("“", '"').replace("”", '"').replace("’", "'")
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)          # hyphenation across line breaks
    return re.sub(r"\s+", " ", s).strip().lower()


def check_record(r: dict) -> list[str]:
    errs = []
    for k in ("term", "section", "quote", "definition_kind", "tier"):
        if r.get(k) in (None, ""):
            errs.append(f"missing {k}")
    if r.get("definition_kind") not in ("quote", "paraphrase", "none"):
        errs.append(f"definition_kind {r.get('definition_kind')!r}")
    if str(r.get("tier")) not in ("1", "2", "3"):
        errs.append(f"tier {r.get('tier')!r}")
    for k in ("alt_labels", "broader", "is_part_of", "related"):
        if r.get(k) is not None and not isinstance(r.get(k), list):
            errs.append(f"{k} is not a list")
    if r.get("definition_kind") != "none" and not (r.get("definition") or "").strip():
        errs.append("definition empty")
    return errs


def lower_first(t: str) -> str:
    """First letter lower case, unless the term starts with an acronym (G/S areal, ROS-analyse, NIB-bjelke)."""
    t = re.sub(r"\s+", " ", (t or "").strip())
    if not t:
        return t
    head = re.split(r"[\s,(-]", t, maxsplit=1)[0]
    letters = [ch for ch in head if ch.isalpha()]
    return t if len(letters) >= 2 and all(ch.isupper() for ch in letters) else t[0].lower() + t[1:]


def collect(manifest_path, workbook, out, source, contact=None, kortnavn=None, title=None) -> dict:
    man = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    v = read_workbook(workbook)
    wb = openpyxl.load_workbook(workbook)
    ws = wb["vokabular"]
    if kortnavn or title:
        for r in range(1, 30):
            a = normalise_header(ws.cell(r, 1).value)
            if kortnavn and a.startswith("kortnavn"):
                ws.cell(r, 2).value = kortnavn
            elif title and a == "dct:title":
                ws.cell(r, 2).value = title
    col = {f: openpyxl.utils.column_index_from_string(L) for f, L in v.columns["vokabular"].items()}
    LF = v.label_field
    names = {c.key for c in v.concepts}
    by_label = {c.get(LF).strip().lower(): c.key for c in v.concepts if c.get(LF)}
    next_row = max((c.row for c in v.concepts), default=None)
    if next_row is None:
        next_row = next(r for r in range(1, 40) if str(ws.cell(r, 1).value or "").strip() == "intern_identifikator")
    today = date.today().isoformat()
    report = {"chapters": [], "accepted": [], "rejected": [], "existing": [], "unresolved_relations": []}
    rows = []
    for ch in man["chapters"]:
        res = Path(ch["result"])
        if not res.exists():
            report["chapters"].append({"id": ch["id"], "status": "no result"})
            continue
        text = _norm(Path(ch["result"]).parent.parent.joinpath("chapters", f"{ch['id']}.txt").read_text(encoding="utf-8"))
        recs = json.loads(res.read_text(encoding="utf-8"))
        n_ok = 0
        for r in recs:
            errs = check_record(r)
            if r.get("quote") and _norm(r["quote"]) not in text:
                errs.append("quote not found in chapter")
            term = lower_first(r.get("term") or "")
            if errs:
                report["rejected"].append({"chapter": ch["id"], "term": term, "errors": errs})
                continue
            if term.lower() in by_label:
                report["existing"].append({"chapter": ch["id"], "term": term, "concept": by_label[term.lower()]})
                continue
            name, k = local_name(term), 1
            while name in names:
                k += 1
                name = f"{local_name(term)}{k}"
            names.add(name)
            by_label[term.lower()] = name
            rows.append((ch, r, term, name))
            n_ok += 1
        report["chapters"].append({"id": ch["id"], "status": "collected", "records": len(recs), "accepted": n_ok})
    for ch, r, term, name in rows:
        rel_names = {}
        for fld in ("broader", "is_part_of", "related"):
            out_names = []
            for t in r.get(fld) or []:
                n = by_label.get(lower_first(t).lower())
                if n:
                    out_names.append(n)
                else:
                    report["unresolved_relations"].append({"concept": name, "field": fld, "target": t})
            rel_names[fld] = ", ".join(out_names) or None
        kind = r["definition_kind"]
        chapter_text = _norm(Path(ch["result"]).parent.parent.joinpath("chapters", f"{ch['id']}.txt").read_text(encoding="utf-8"))
        if kind == "quote" and _norm(r.get("definition") or "") not in chapter_text:
            kind = "paraphrase"          # a "quote" must be verbatim; otherwise it counts as a paraphrase
            report.setdefault("downgraded", []).append({"concept": name, "term": term})
        where = f"{man['title']} kap. {r['section']}"
        note = {"quote": f"[kilde] Definisjon sitert fra {where}.",
                "paraphrase": f"[omskrivning] Definisjon fra {where}.",
                "none": f"[mangler] definisjon. [kilde] Innført i {where}."}[kind]
        if r.get("cue") and any(rel_names.values()):
            note += f" [kilde] Relasjon begrunnet med «{r['cue']}»."
        unresolved = [x["target"] for x in report["unresolved_relations"] if x["concept"] == name]
        if unresolved:
            note += " [usikker] Relasjon til " + ", ".join(f"«{t}»" for t in unresolved) + " ikke funnet."
        if r.get("uncertain"):
            note += f" [usikker] {r['uncertain']}"
        f = {"uri": name, LF: term, "def_" + LF[6:]: (r.get("definition") or "").strip() or None,
             "notation": r.get("notation") or None, "alt_" + LF[6:]: ", ".join(r.get("alt_labels") or []) or None,
             "broader": rel_names["broader"], "is_part_of": rel_names["is_part_of"], "related": rel_names["related"],
             "source": source, "relationship_with_source": {"quote": "direct-from-source", "paraphrase": "derived-from-source"}.get(kind),
             "editorial_note": note, "status": "kandidat", "contact_point": contact, "created": today, "tier": str(r["tier"])}
        next_row += 1
        for fld, val in f.items():
            if fld in col and val is not None:
                ws.cell(next_row, col[fld]).value = val
        report["accepted"].append({"chapter": ch["id"], "term": term, "concept": name, "section": r["section"]})
    fit_table(wb)
    apply_formulas(wb)
    wb.save(out)
    return report


def report_md(report: dict) -> str:
    L = ["# Extraction report", "", "| Chapter | Status | Records | Accepted |", "| --- | --- | --- | --- |"]
    L += [f"| {c['id']} | {c['status']} | {c.get('records', '')} | {c.get('accepted', '')} |" for c in report["chapters"]]
    L += ["", f"## Accepted ({len(report['accepted'])})", ""] + [f"- {a['term']} ({a['concept']}, kap. {a['section']})" for a in report["accepted"]]
    L += ["", f"## Rejected ({len(report['rejected'])})", ""] + [f"- {a['term']}: {'; '.join(a['errors'])}" for a in report["rejected"]]
    L += ["", f"## Definitions marked as quote but not verbatim, kept as paraphrase ({len(report.get('downgraded', []))})", ""] + [f"- {a['term']} ({a['concept']})" for a in report.get("downgraded", [])]
    L += ["", f"## Already in the workbook ({len(report['existing'])})", ""] + [f"- {a['term']} → {a['concept']}" for a in report["existing"]]
    L += ["", f"## Relations not resolved ({len(report['unresolved_relations'])})", ""] + [f"- {a['concept']} {a['field']} «{a['target']}»" for a in report["unresolved_relations"]]
    return "\n".join(L) + "\n"

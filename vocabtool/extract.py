"""Extraction of concepts from text (TXT converted from PDF), one LLM agent per chapter.

    prepare  TXT -> chapters or sections (one file each) + one prompt per chunk + manifest.json
    (run)    an agent per chapter reads its prompt and writes <chapter id>.json (records, see RECORD_FIELDS)
    collect  records -> schema check, quote check -> new rows in a v9 workbook + report

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
from .lists import save_workbook

# ---------------------------------------------------------------- split
# Numbered headings, with or without a space after the number: "5Tiltak", "5 Tiltak", "2.5.3Hovedinspeksjon".
# Appendices: "<word> B" on a line of its own, with sections "B.3", "B.3.1Armering…".
# A line that ends in a page number is a table-of-contents entry, not a heading.
HEADING_RE = re.compile(r"^(?P<num>\d{1,2}(?:\.\d{1,2}){0,4})\s?(?P<title>[A-ZÆØÅ][^\n]*[a-zæøå][^\n]*?)\s*$")
# appendix section heading: letter and number (A.1, B.2.3)
APPENDIX_SECTION_RE = re.compile(r"^(?P<num>[A-Z](?:\.\d{1,2}){1,4})\.?\s?(?P<title>[A-ZÆØÅ][^\n]*[a-zæøå][^\n]*?)\s*$")
# a page number at the end of a line (table of contents entry)
TOC_ENTRY_RE = re.compile(r"\s\d{1,4}\s*$")
# words that start an appendix heading (default of --appendix-words)
APPENDIX_WORDS = ("Tillegg", "Vedlegg", "Appendix", "Annex")


def _depth(num: str) -> int:
    """Heading depth of a section number: "5" -> 1, "5.2" -> 2."""
    return num.count(".") + 1


def _num_key(num: str) -> tuple:
    """Sort key for section numbers ("5.10" after "5.9"; letters for appendices)."""
    return tuple(int(x) if x.isdigit() else ord(x) for x in num.split("."))


def split_text(path, level: int = 1, appendix_words=APPENDIX_WORDS, start_line: int | None = None,
               min_chars: int = 0) -> list[dict]:
    """Split a text into chunks at headings of depth <= level (1 = chapters, 2 = sections such as 5.2).

    Headings are accepted only in order: a chapter must follow the previous one (5 after 4), a section must lie
    inside the current chapter and come after the previous section. When chapter 1 (or appendix A) appears again before chapter 2 (or B),
    everything before it is dropped, which removes front matter such as a foreword or the table of contents.
    Numbered lines inside tables ("4 Aluminium" after chapter 7) are out of order and therefore ignored.
    start_line (1-based) skips everything before it. Chunks shorter than min_chars are merged into the next chunk
    of the same chapter.
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    app_re = re.compile(rf"^(?:{'|'.join(map(re.escape, appendix_words))}) (?P<num>[A-Z])\.?\s*$")
    heads = []                                     # (line index, number, title, depth)
    chapter, appendix, last_section, highest = None, None, None, 0
    for i, line in enumerate(lines):
        if start_line and i + 1 < start_line:
            continue
        s = line.strip()
        if not s or TOC_ENTRY_RE.search(s):
            continue
        m = app_re.match(s)
        if m:
            letter = m.group("num")
            if letter == "A" and appendix in (None, "A"):
                heads = [h for h in heads if not h[1][0].isalpha()]      # appendix A again: drop earlier appendices
            elif appendix is None or ord(letter) != ord(appendix) + 1:
                continue
            appendix, chapter, last_section = letter, None, None
            title = next((l.strip() for l in lines[i + 1:i + 4] if l.strip()), "")[:80]
            heads.append((i, letter, title, 1))
            continue
        m = HEADING_RE.match(s) or (appendix and APPENDIX_SECTION_RE.match(s))
        if not m or len(m.group("title")) < 4 or m.group("title").endswith("."):    # "1. Lov om …" is a list item
            continue
        num, title, d = m.group("num"), m.group("title").strip(), _depth(m.group("num"))
        if d == 1 and num.isdigit():
            if num == "1" and highest <= 1:                              # restart: front matter before this
                heads, appendix = [], None
            elif chapter is None or int(num) != int(chapter) + 1 or appendix:
                continue
            chapter, last_section, highest = num, None, max(highest, int(num))
            heads.append((i, num, title, 1))
        elif d <= level:
            owner = num.split(".")[0]
            if owner != (chapter if num[0].isdigit() else appendix):
                continue
            if last_section and _num_key(num) <= _num_key(last_section):
                continue
            last_section = num
            heads.append((i, num, title, d))
    chunks = []
    for k, (i, num, title, d) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        text = "\n".join(lines[i:end]).strip()
        cid = ("ch" if num[0].isdigit() else "app") + num
        chunks.append({"id": cid, "number": num, "title": title, "start_line": i + 1, "end_line": end,
                       "chars": len(text), "text": text})
    if min_chars:
        merged = []
        for ch in chunks:
            prev = merged[-1] if merged else None
            same = prev and prev["number"].split(".")[0] == ch["number"].split(".")[0]
            if prev and same and prev["chars"] < min_chars:
                prev["text"] += "\n\n" + ch["text"]
                prev["end_line"], prev["chars"] = ch["end_line"], len(prev["text"])
                prev["title"] = f"{prev['title']} – {ch['title']}"[:120]
            else:
                merged.append(dict(ch))
        chunks = merged
    return chunks


# ---------------------------------------------------------------- prompt
# the fields of one agent record and what each must hold (also shown to the agent in the prompt)
RECORD_FIELDS = {
    "term": "anbefalt term på hovedspråket, med liten forbokstav unntatt akronymer",
    "section": "avsnittsnummeret der begrepet defineres eller innføres, f.eks. 5.2 eller B.3.1",
    "quote": "ordrett setning fra kapitlet som definerer eller innfører begrepet (kopier tegn for tegn)",
    "definition": "definisjon på hovedspråket, genus/differentia, liten forbokstav, uten punktum til slutt; tom hvis kilden ikke gir grunnlag",
    "definition_kind": "\"quote\" hvis definisjonen er ordrett fra kilden, \"paraphrase\" hvis omskrevet, \"none\" hvis tom",
    "type": "1, 2 eller 3",
    "alt_labels": "liste med tillatte termer og akronymer fra kilden (kan være tom)",
    "notation": "kode fra kilden, ellers null",
    "broader": "liste med termer (ikke navn) for overbegreper, bare når kilden uttrykker det",
    "is_part_of": "liste med termer for helheter begrepet er del av, bare når kilden uttrykker det",
    "related": "liste med termer for relaterte begreper, bare når kilden kobler dem uttrykkelig",
    "cue": "ordene i kilden som begrunner relasjonene (f.eks. «omfatter», «består av»), ellers null",
    "uncertain": "kort beskrivelse av det du er usikker på (type, relasjon, sammenslåing), ellers null",
}

# prompt template for one chunk; placeholders are filled by prepare (--prompt-template replaces it)
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


def prepare(txt, out_dir, instructions, kortnavn, title_doc, known_workbooks=(), only=None, level=1,
            appendix_words=APPENDIX_WORDS, start_line=None, min_chars=0, prompt_template=None) -> list[dict]:
    """prompt_template: a file with the same {placeholders} as PROMPT (title_doc, kortnavn, number, title, text,
    known, instructions, fields, result_path); by default the built-in Norwegian prompt."""
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
    template = Path(prompt_template).read_text(encoding="utf-8") if prompt_template else PROMPT
    chunks = split_text(txt, level=level, appendix_words=appendix_words, start_line=start_line, min_chars=min_chars)
    manifest = []
    for ch in chunks:
        if only and ch["id"] not in only:
            continue
        (out / "chapters" / f"{ch['id']}.txt").write_text(ch["text"], encoding="utf-8")
        result = out / "results" / f"{ch['id']}.json"
        prompt = template.format(title_doc=title_doc, kortnavn=kortnavn, number=ch["number"], title=ch["title"],
                               text=ch["text"], known="\n".join(known) or "(ingen)", instructions=rules,
                               fields=fields, result_path=result)
        (out / "prompts" / f"{ch['id']}.md").write_text(prompt, encoding="utf-8")
        manifest.append({k: ch[k] for k in ("id", "number", "title", "start_line", "end_line", "chars")}
                        | {"prompt": str(out / "prompts" / f"{ch['id']}.md"), "result": str(result),
                           "prompt_chars": len(prompt), "done": result.exists()})
    (out / "manifest.json").write_text(json.dumps({"source": str(txt), "kortnavn": kortnavn, "title": title_doc, "level": level,
                                                   "chapters": manifest}, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest


# ---------------------------------------------------------------- collect
def _norm(s: str) -> str:
    """Normalised text for the quote check: quotes, hyphenation at line breaks, whitespace and case do not matter."""
    s = s.replace(" ", " ").replace("«", '"').replace("»", '"').replace("“", '"').replace("”", '"').replace("’", "'")
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)          # hyphenation across line breaks
    return re.sub(r"\s+", " ", s).strip().lower()


def _key(term: str) -> str:
    """Match key for terms: case, spaces, hyphens, slashes and commas do not matter ("ROS-analyse" = "ROS analyse")."""
    return re.sub(r"[\s\-/,]+", " ", (term or "")).strip().lower()


def check_record(r: dict) -> list[str]:
    """Check one agent record against RECORD_FIELDS.

    Records written with the former field name tier are accepted (renamed to type).

    Returns:
        The problems found; an empty list means the record is valid.
    """
    errs = []
    if "type" not in r and "tier" in r:          # records written before the rename
        r["type"] = r.pop("tier")
    for k in ("term", "section", "quote", "definition_kind", "type"):
        if r.get(k) in (None, ""):
            errs.append(f"missing {k}")
    if r.get("definition_kind") not in ("quote", "paraphrase", "none"):
        errs.append(f"definition_kind {r.get('definition_kind')!r}")
    if str(r.get("type")) not in ("1", "2", "3"):
        errs.append(f"type {r.get('type')!r}")
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


def collect(manifest_path, workbook, out, source, contact=None, kortnavn=None, title=None, link_workbooks=()) -> dict:
    """Check the agents' records and add new concepts to the workbook.

    - A record is rejected if it does not match the record format or its quote is not in the chunk.
    - A term already in the workbook is not added again. If that concept has no definition and the record has
      one, the definition is written to <out>.suggestions.json (set-fields format) for review instead.
    - A term that appears twice in the run is added once; the repeat is reported.
    - link_workbooks: other v9 vocabularies. A new term that matches exactly one concept there gets
      skos:exactMatch to it and, if that concept has a definition from a source (not derived), its definition is
      copied with that concept as dct:source (merge rule). Relation targets found only there are reported.
    """
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
    DF = v.def_field
    existing = {c.key: c for c in v.concepts}
    names = set(existing)
    by_label = {_key(c.get(LF)): c.key for c in v.concepts if c.get(LF)}
    linked = {}                                     # lower-case label -> [(kortnavn, name, uri, definition or None)]
    for lw in link_workbooks:
        lv = read_workbook(lw)
        base = lv.scheme_uri.rstrip("/")
        for c in lv.concepts:
            if not c.get(lv.label_field):
                continue
            real_def = c.get(lv.def_field) if c.get(lv.def_field) and "[avledet]" not in (c.get("editorial_note") or "") else None
            linked.setdefault(_key(c.get(lv.label_field)), []).append((lv.kortnavn, c.key, f"{base}/{c.key}", real_def))
    next_row = max((c.row for c in v.concepts), default=None)
    if next_row is None:
        next_row = next(r for r in range(1, 40) if str(ws.cell(r, 1).value or "").strip() == "intern_identifikator")
    today = date.today().isoformat()
    report = {"chapters": [], "accepted": [], "rejected": [], "existing": [], "duplicates": [], "linked": [],
              "downgraded": [], "unresolved_relations": [], "suggestions": {}}
    rows, batch, texts = [], {}, {}

    def where_of(r):
        """Source reference for the editorial note: "<document> kap. <section>"."""
        return f"{man['title']} kap. {r['section']}"

    for ch in man["chapters"]:
        res = Path(ch["result"])
        if not res.exists():
            report["chapters"].append({"id": ch["id"], "status": "no result"})
            continue
        texts[ch["id"]] = text = _norm(res.parent.parent.joinpath("chapters", f"{ch['id']}.txt").read_text(encoding="utf-8"))
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
            key = _key(term)
            if key in batch:
                report["duplicates"].append({"chapter": ch["id"], "term": term, "first": batch[key]})
                continue
            if key in by_label:
                cname = by_label[key]
                entry = {"chapter": ch["id"], "term": term, "concept": cname, "suggested": False}
                d = (r.get("definition") or "").strip()
                if d and not existing[cname].get(DF) and r["definition_kind"] != "none":
                    quoted = r["definition_kind"] == "quote" and _norm(d) in text
                    report["suggestions"][cname] = {
                        DF: d, "source": source,
                        "relationship_with_source": "direct-from-source" if quoted else "derived-from-source",
                        "editorial_note+": (f"[kilde] Definisjon sitert fra {where_of(r)}." if quoted
                                            else f"[omskrivning] Definisjon fra {where_of(r)}.")}
                    entry["suggested"] = True
                report["existing"].append(entry)
                continue
            name, k = local_name(term), 1
            while name in names:
                k += 1
                name = f"{local_name(term)}{k}"
            names.add(name)
            by_label[key] = name
            batch[key] = ch["id"]
            rows.append((ch, r, term, name))
            n_ok += 1
        report["chapters"].append({"id": ch["id"], "status": "collected", "records": len(recs), "accepted": n_ok})

    for ch, r, term, name in rows:
        rel_names, notes = {}, []
        for fld in ("broader", "is_part_of", "related"):
            out_names = []
            for t in r.get(fld) or []:
                n = by_label.get(_key(t))
                if n:
                    out_names.append(n)
                    continue
                hits = linked.get(_key(t), [])
                elsewhere = ", ".join(f"{k} ({c})" for k, c, _, _ in hits)
                report["unresolved_relations"].append({"concept": name, "field": fld, "target": t, "found_in": elsewhere})
                notes.append(f"[usikker] {fld} «{t}» finnes ikke i vokabularet" + (f", men i {elsewhere}." if elsewhere else "."))
            rel_names[fld] = ", ".join(out_names) or None
        kind = r["definition_kind"]
        definition = (r.get("definition") or "").strip() or None
        if kind == "quote" and _norm(definition or "") not in texts[ch["id"]]:
            kind = "paraphrase"          # a "quote" must be verbatim; otherwise it counts as a paraphrase
            report["downgraded"].append({"concept": name, "term": term})
        src, rel = source, {"quote": "direct-from-source", "paraphrase": "derived-from-source"}.get(kind)
        note = {"quote": f"[kilde] Definisjon sitert fra {where_of(r)}.",
                "paraphrase": f"[omskrivning] Definisjon fra {where_of(r)}.",
                "none": f"[mangler] definisjon. [kilde] Innført i {where_of(r)}."}[kind]
        exact = None
        hits = linked.get(_key(term), [])
        if len(hits) == 1:                              # merge rule: own concept, linked to the other vocabulary
            k_, cname, uri, ldef = hits[0]
            exact = uri
            if ldef:
                definition, src, rel = ldef, uri, "direct-from-source"
                note = f"[kilde] Definisjon kopiert fra {k_} ({cname}). [kilde] Innført i {where_of(r)}."
            report["linked"].append({"concept": name, "to": uri, "definition_copied": bool(ldef)})
        elif len(hits) > 1:
            notes.append("[usikker] Samme term i " + ", ".join(f"{k} ({c})" for k, c, _, _ in hits) + "; ikke koblet.")
        if r.get("cue") and any(rel_names.values()):
            note += f" [kilde] Relasjon begrunnet med «{r['cue']}»."
        note = " ".join([note] + notes + ([f"[usikker] {r['uncertain']}"] if r.get("uncertain") else []))
        f = {"uri": name, LF: term, DF: definition,
             "notation": r.get("notation") or None, "alt_" + LF[6:]: ", ".join(r.get("alt_labels") or []) or None,
             "broader": rel_names["broader"], "is_part_of": rel_names["is_part_of"], "related": rel_names["related"],
             "exact_match": exact, "source": src, "relationship_with_source": rel,
             "editorial_note": note, "status": "kandidat", "contact_point": contact, "created": today, "type": str(r["type"])}
        next_row += 1
        for fld, val in f.items():
            if fld in col and val is not None:
                ws.cell(next_row, col[fld]).value = val
        report["accepted"].append({"chapter": ch["id"], "term": term, "concept": name, "section": r["section"]})
    fit_table(wb)
    apply_formulas(wb)
    save_workbook(wb, out)
    if report["suggestions"]:
        Path(out).with_suffix(".suggestions.json").write_text(json.dumps(report["suggestions"], ensure_ascii=False, indent=1), encoding="utf-8")
    return report


def report_md(report: dict) -> str:
    """Markdown report of extract collect: chapters, accepted, rejected, downgraded quotes, existing, links."""
    L = ["# Extraction report", "", "| Chapter | Status | Records | Accepted |", "| --- | --- | --- | --- |"]
    L += [f"| {c['id']} | {c['status']} | {c.get('records', '')} | {c.get('accepted', '')} |" for c in report["chapters"]]
    L += ["", f"## Accepted ({len(report['accepted'])})", ""] + [f"- {a['term']} ({a['concept']}, kap. {a['section']})" for a in report["accepted"]]
    L += ["", f"## Rejected ({len(report['rejected'])})", ""] + [f"- {a['term']}: {'; '.join(a['errors'])}" for a in report["rejected"]]
    L += ["", f"## Definitions marked as quote but not verbatim, kept as paraphrase ({len(report.get('downgraded', []))})", ""] + [f"- {a['term']} ({a['concept']})" for a in report["downgraded"]]
    L += ["", f"## Already in the workbook ({len(report['existing'])})", ""] + [f"- {a['term']} → {a['concept']}" + (" (definition suggested in .suggestions.json)" if a.get("suggested") else "") for a in report["existing"]]
    L += ["", f"## Repeated in this run, added once ({len(report['duplicates'])})", ""] + [f"- {a['term']} ({a['chapter']}; first in {a['first']})" for a in report["duplicates"]]
    L += ["", f"## Linked to another vocabulary ({len(report['linked'])})", ""] + [f"- {a['concept']} → {a['to']}" + (" (definition copied)" if a["definition_copied"] else "") for a in report["linked"]]
    L += ["", f"## Relations not resolved ({len(report['unresolved_relations'])})", ""] + [f"- {a['concept']} {a['field']} «{a['target']}»" + (f" (found in {a['found_in']})" if a.get("found_in") else "") for a in report["unresolved_relations"]]
    return "\n".join(L) + "\n"

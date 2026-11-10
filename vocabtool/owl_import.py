"""Add the classes of OWL ontologies as concepts to a v8 workbook, merging with existing concepts.

Merging (an existing concept is the same as a class):
- same main-language label or alt label (normalised: case, spaces, punctuation, text in parentheses), and the
  label is used by only one class in the file; or
- a reviewed merge map (JSON: class IRI -> concept name) for spelling or wording variants, e.g. classes with the
  same code. The class label is then recorded in the editorial note.
A merged concept gets the class IRI in skos:exactMatch. Notation (from `kode`), English label and broader are
filled only where empty; differences are listed as conflicts in the log, never overwritten.

New concepts (one row per class):
- label from rdfs:label@no/nb (first letter lower case unless an acronym), English label from @en; a class
  without a label gets a term from its IRI, flagged in the editorial note
- a label used by several classes, or already used in the workbook, gets the parent class as qualifier
  ("fundament, pilar"), in both languages
- notation = `kode`, broader = parent class, exactMatch = class IRI, source = ontology IRI,
  editorial note with chapter/section (`kapittel`, `avsnitt`) and "[mangler] definisjon"
- status kandidat, created today, contact point if given
- --link <v8 workbook>: a new concept whose label matches exactly one concept with a definition there gets
  exactMatch to it, its definition copied, source = that concept and relationshipWithSource direct-from-source

Skipped: deprecated classes, and the technical root (the single top class of a file, e.g. "Rotobjekt for v440"),
unless keep_root is set. Code values (individuals) and properties are not imported.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import openpyxl
from rdflib import Graph, Literal, OWL, RDF, RDFS, URIRef

from .reader import read_workbook, normalise_header
from .template_ext import fit_table, apply_formulas
from .uri import local_name


def norm(s) -> str:
    return re.sub(r"[\s\-/,]+", " ", re.sub(r"\(.*?\)", "", str(s or ""))).strip().lower()


def lower_first(t: str | None) -> str | None:
    t = re.sub(r"\s+", " ", (t or "").strip())
    if not t:
        return t
    w = re.split(r"[\s/,(]", t, maxsplit=1)[0]
    letters = [ch for ch in w if ch.isalpha()]
    return t if len(letters) >= 2 and all(ch.isupper() for ch in letters) else t[0].lower() + t[1:]


def _label(g, x, langs):
    ls = [l for l in g.objects(x, RDFS.label) if isinstance(l, Literal)]
    for lang in langs:
        hit = [str(l) for l in ls if (l.language or "") == lang]
        if hit:
            return hit[0]
    return None


def read_classes(path) -> tuple[str, dict]:
    """(ontology IRI, {class IRI: {no, en, parents, kode, kapittel, avsnitt, deprecated}})"""
    g = Graph().parse(str(path))
    ont = next(g.subjects(RDF.type, OWL.Ontology), None)
    cls = {c for c in g.subjects(RDF.type, OWL.Class) if isinstance(c, URIRef)}
    out = {}
    for c in cls:
        lit = {str(p).rsplit("#", 1)[-1].rsplit("/", 1)[-1]: str(o) for p, o in g.predicate_objects(c)
               if isinstance(o, Literal) and p != RDFS.label}
        out[str(c)] = {"iri": str(c), "no": _label(g, c, ("no", "nb", "")), "en": _label(g, c, ("en",)),
                       "parents": sorted(str(o) for o in g.objects(c, RDFS.subClassOf) if isinstance(o, URIRef)),
                       "kode": lit.get("kode"), "kapittel": lit.get("kapittel"), "avsnitt": lit.get("avsnitt"),
                       "deprecated": (c, OWL.deprecated, None) in g}
    return str(ont) if ont else str(path), out


def owl_import(workbook, owls: list, out, *, link=None, merge_map=None, contact=None, keep_root=False,
               kortnavn=None, title=None) -> dict:
    v = read_workbook(workbook)
    wb = openpyxl.load_workbook(workbook)
    ws = wb["vokabular"]
    if kortnavn or title:   # new vocabulary from an empty template: scheme rows kortnavn / dct:title
        for r in range(1, 30):
            a = normalise_header(ws.cell(r, 1).value)
            if kortnavn and a.startswith("kortnavn"):
                ws.cell(r, 2).value = kortnavn
            elif title and a == "dct:title":
                ws.cell(r, 2).value = title
    col = {f: openpyxl.utils.column_index_from_string(L) for f, L in v.columns["vokabular"].items()}
    fuzzy = json.loads(Path(merge_map).read_text(encoding="utf-8")) if merge_map else {}
    lv = read_workbook(link) if link else None
    link_idx = {}
    if lv:
        for c in lv.concepts:
            if c.get(lv.label_field):
                link_idx.setdefault(norm(c.get(lv.label_field)), []).append(c)
    LF, EN = v.label_field, "label_en"
    today = date.today().isoformat()

    rows, idx = {}, {}
    for c in v.concepts:
        rows[c.key] = {"row": c.row, "fields": dict(c.fields), "broader": list(c.relations["broader"]), "new": False}
        for t in [c.get(LF), *(c.get("alt_" + LF[6:]) or "").split(",")]:
            if t and t.strip():
                idx.setdefault(norm(t), c.key)
    if v.concepts:
        next_row = max(c.row for c in v.concepts)
    else:   # empty template: data start after the row with technical names (intern_identifikator)
        next_row = next(r for r in range(1, 40) if str(ws.cell(r, 1).value or "").strip() == "intern_identifikator")
    log = {"merged": [], "new": [], "skipped": [], "linked": [], "conflicts": []}

    for owl in owls:
        ont, C = read_classes(owl)
        onto_short = ont.rstrip("/#").rsplit("/", 1)[-1]
        for d in C.values():
            d["from_iri"] = (d["no"] or "").strip() in ("", "-")
            d["label"] = lower_first(d["no"] if not d["from_iri"] else d["iri"].rsplit("#", 1)[-1].replace("_", " "))
        tops = [i for i, d in C.items() if not any(p in C for p in d["parents"])]
        roots = set(tops) if len(tops) == 1 and not keep_root else set()
        keep = {i: d for i, d in C.items() if not d["deprecated"] and i not in roots}
        for i, d in C.items():
            if i not in keep:
                log["skipped"].append({"iri": i, "label": d["no"], "why": "deprecated" if d["deprecated"] else "technical root"})
        counts = {}
        for d in keep.values():
            counts[norm(d["label"])] = counts.get(norm(d["label"]), 0) + 1

        def parent_of(d):
            ps = [keep[p] for p in d["parents"] if p in keep]
            return ps[0] if ps else None

        name_of = {}
        for i, d in sorted(keep.items(), key=lambda x: (x[1]["label"], x[0])):
            n = norm(d["label"])
            if i in fuzzy:
                if fuzzy[i] not in rows:
                    raise ValueError(f"merge map: no concept named {fuzzy[i]!r} (for {i})")
                name_of[i], d["merge"], d["fuzzy"] = fuzzy[i], True, True
            elif counts[n] == 1 and n in idx and not d["from_iri"]:
                name_of[i], d["merge"] = idx[n], True
            else:
                d["merge"] = False
                label = d["label"]
                if counts[n] > 1 or n in idx:
                    p = parent_of(d)
                    label = f"{d['label']}, {lower_first(p['label']) if p else onto_short}"
                    if d["en"] and d["en"].strip() != "-":
                        d["en"] = f"{d['en'].strip()}, {lower_first(p['en']) if p and p['en'] else onto_short}"
                base, name, k = local_name(label), local_name(label), 1
                while name in rows or name in name_of.values():
                    k += 1
                    name = f"{base}{d['kode'] if d['kode'] not in (None, '-') and k == 2 else k}"
                d["label"], name_of[i] = label, name

        # stable, readable order: depth-first from the top classes, siblings by code, then label
        def sort_key(d):
            k = d["kode"] if d["kode"] not in (None, "-") else ""
            return (re.sub(r"\d+", lambda m: m.group(0).zfill(6), k) if k else "~", d["label"], d["iri"])
        children = {}
        for d in keep.values():
            p = parent_of(d)
            children.setdefault(p["iri"] if p else None, []).append(d)
        order, stack = [], sorted(children.get(None, []), key=sort_key, reverse=True)
        while stack:
            d = stack.pop()
            order.append(d["iri"])
            stack += sorted(children.get(d["iri"], []), key=sort_key, reverse=True)
        order += sorted((i for i in keep if i not in set(order)), key=lambda i: sort_key(keep[i]))   # cycles
        for i in order:
            d = keep[i]
            p = parent_of(d)
            parent_name = name_of.get(p["iri"]) if p else None
            notation = d["kode"] if d["kode"] not in (None, "-", "") else None
            en = lower_first(d["en"]) if d["en"] and d["en"].strip() != "-" else None
            if d["merge"]:
                r = rows[name_of[i]]
                f = r["fields"]
                em = [x.strip() for x in (f.get("exact_match") or "").split(",") if x.strip()]
                if i not in em:
                    em.append(i)
                f["exact_match"] = ", ".join(em)
                filled = ["exact_match"]
                if notation and not f.get("notation"):
                    f["notation"] = notation; filled.append("notation")
                elif notation and f.get("notation") != notation:
                    log["conflicts"].append({"concept": name_of[i], "field": "notation", "workbook": f.get("notation"), "owl": notation, "iri": i})
                if en and not f.get(EN):
                    f[EN] = en; filled.append(EN)
                if parent_name and not r["broader"]:
                    f["broader"] = parent_name; r["broader"] = [parent_name]; filled.append("broader")
                elif parent_name and parent_name not in r["broader"]:
                    log["conflicts"].append({"concept": name_of[i], "field": "broader", "workbook": r["broader"], "owl": parent_name, "iri": i})
                if d.get("fuzzy"):
                    f["editorial_note"] = ((f.get("editorial_note") or "") +
                                           f" [merknad] OWL-klasse: «{(d['no'] or '').strip()}» ({i.rsplit('#', 1)[-1]}).").strip()
                    filled.append("editorial_note")
                r.setdefault("changed", set()).update(filled)
                log["merged"].append({"concept": name_of[i], "iri": i, "filled": filled})
                continue
            place = ", ".join(x for x in (d["kapittel"] and f"kap. {d['kapittel']}", d["avsnitt"] and f"avsnitt {d['avsnitt']}") if x)
            note = f"[kilde] OWL-klasse {i.rsplit('#', 1)[-1]} i {onto_short}{' (' + place + ')' if place else ''}. [mangler] definisjon."
            if d["from_iri"]:
                note += " [merknad] Ingen rdfs:label i ontologien; termen er laget fra IRI-en."
            f = {"uri": name_of[i], LF: d["label"], EN: en, "notation": notation, "broader": parent_name,
                 "exact_match": i, "source": ont, "editorial_note": note, "status": "kandidat",
                 "contact_point": contact, "created": today}
            hits = link_idx.get(norm(d["label"]), [])
            if lv and len(hits) == 1 and hits[0].get(lv.def_field):
                t = hits[0]
                turi = f"{lv.scheme_uri.rstrip('/')}/{t.key}"
                f.update({v.def_field: t.get(lv.def_field), "exact_match": f"{i}, {turi}", "source": turi,
                          "relationship_with_source": "direct-from-source",
                          "editorial_note": f"[kilde] Definisjon kopiert fra {lv.kortnavn} ({t.key}). " + note.replace(" [mangler] definisjon.", "")})
                log["linked"].append({"concept": name_of[i], "to": turi})
            next_row += 1
            rows[name_of[i]] = {"row": next_row, "fields": f, "broader": [parent_name] if parent_name else [],
                                "new": True, "changed": set(f)}
            idx.setdefault(norm(d["label"]), name_of[i])
            log["new"].append({"concept": name_of[i], "label": d["label"], "iri": i, "broader": parent_name})

    for r in rows.values():
        for fld in r.get("changed", ()):
            if fld in col and fld not in ("identifier", "change_hash", "created_by"):
                ws.cell(r["row"], col[fld]).value = r["fields"].get(fld)
    fit_table(wb)
    apply_formulas(wb)
    wb.save(out)
    return log

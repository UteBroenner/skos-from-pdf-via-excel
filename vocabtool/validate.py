"""Deterministic checks on a vocabulary read by reader.read_workbook.

Rule codes are local to this tool (prefix VT-). Where a check corresponds to a
rule in the SKOS field instructions, the instruction ID is given in `ref`.
Severity: error = must be fixed before publishing; warning = review;
info = expected gap (e.g. nn labels left for the expert) or heuristic hint.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict

from .reader import Vocabulary, RELATION_FIELDS, label_fields, split_multi
from .uri import LOCAL_NAME_RE, cross_language_homonyms, expected_name

STATUS_VALUES = {"kandidat", "gjeldende", "utdatert", "forkastet"}
TIERS = {"1", "2", "3"}


@dataclass
class Finding:
    rule: str
    severity: str
    key: str | None
    sheet: str | None
    row: int | None
    message: str
    ref: str = ""

    def as_dict(self):
        return asdict(self)


RULES = {
    "VT-ID-FORMAT": ("error", "ID does not match <kortnavn>-NNNN", "template v8 col A"),
    "VT-ID-DUPLICATE": ("error", "ID used on more than one row", ""),
    "VT-URI-MISSING": ("error", "concept name for the URI (column B) missing; run `vocabtool uri` to generate it from the term", "S03"),
    "VT-URI-FORMAT": ("error", "column B must hold only the CamelCase concept name (letters and digits, optionally a language suffix such as -ENUS), e.g. Rekkverk", "S03"),
    "VT-URI-DUPLICATE": ("error", "concept name in column B used on more than one row, so two concepts get the same URI", ""),
    "VT-URI-LABEL": ("info", "concept name in column B differs from the CamelCase form of the main-language term, with -<LANG> suffix where the term means another concept in another language (fine if chosen on purpose)", "S03"),
    "VT-REQ-LABEL": ("error", "prefLabel in the main language missing", ""),
    "VT-REQ-DEF": ("error", "definition in the main language missing", ""),
    "VT-REF-FORMAT": ("error", "relation value is not an ID (v8 relations must use IDs)", ""),
    "VT-REF-DANGLING": ("warning", "relation target not found in this workbook", ""),
    "VT-REF-SELF": ("error", "concept relates to itself", ""),
    "VT-CYCLE-BROADER": ("error", "cycle in skos:broader", "SKOS"),
    "VT-CYCLE-PARTOF": ("error", "cycle in xkos:isPartOf", ""),
    "VT-RELATED-CLASH": ("error", "skos:related to a concept that is also a broader/narrower ancestor", "SKOS S27"),
    "VT-TIER-INVALID": ("warning", "tier is not 1, 2 or 3", ""),
    "VT-TIER-EMPTY": ("info", "tier empty (expected only for source concepts)", "O0"),
    "VT-T1-ISOLATED": ("warning", "Tier 1 concept has no broader, isPartOf or related link (in or out)", ""),
    "VT-T1-BROADER-NON-T1": ("warning", "Tier 1 concept has a broader concept that is not Tier 1 (affects OWL subClassOf)", "O4"),
    "VT-LABEL-DUPLICATE": ("warning", "same main-language prefLabel on more than one concept", "V11/V12"),
    "VT-LABEL-HOMONYM": ("warning", "same term (label or abbreviation) used for different concepts", "V11/V12"),
    "VT-LABEL-NOTED": ("info", "label clash documented in a scope note that names the other concept", ""),
    "VT-LABEL-VARIANT": ("info", "term means a different concept in another regional variant of the language (e.g. en-US vs en-GB)", ""),
    "VT-LABEL-CASE": ("warning", "main-language prefLabel starts with a capital letter (not an acronym)", "S05"),
    "VT-LABEL-GROUPING": ("warning", "label lists several things and has narrower concepts; possibly a table heading, not a concept", ""),
    "VT-STATUS": ("warning", "status not in statusliste", ""),
    "VT-STATUS-LITERAL": ("warning", "status written as RDF literal; use the plain list value", ""),
    "VT-NN-MISSING": ("info", "nn label/definition empty (left for expert)", "S06/S17/S21"),
    "VT-CONTACT": ("warning", "dcat:contactPoint missing", ""),
}


def _f(rule, c=None, msg_extra=""):
    sev, msg, ref = RULES[rule]
    return Finding(rule, sev, c.key if c else None, c.sheet if c else None, c.row if c else None,
                   msg + (f": {msg_extra}" if msg_extra else ""), ref)


def _find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Return each distinct cycle once (as list of nodes)."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour = defaultdict(int)
    cycles, seen = [], set()

    def visit(n, stack):
        colour[n] = GREY
        stack.append(n)
        for m in graph.get(n, []):
            if m not in graph:
                continue
            if colour[m] == GREY:
                cyc = stack[stack.index(m):]
                sig = frozenset(cyc)
                if sig not in seen:
                    seen.add(sig)
                    cycles.append(cyc + [m])
            elif colour[m] == WHITE:
                visit(m, stack)
        stack.pop()
        colour[n] = BLACK

    for n in list(graph):
        if colour[n] == WHITE:
            visit(n, [])
    return cycles


def _ancestors(graph, start):
    out, todo = set(), list(graph.get(start, []))
    while todo:
        n = todo.pop()
        if n in out:
            continue
        out.add(n)
        todo.extend(graph.get(n, []))
    return out


def _noted(c, other_keys: set) -> bool:
    """True if the concept's scope notes (any language) name every other concept by its ID."""
    notes = " ".join(str(v) for f, v in c.fields.items() if f.startswith("scope_note") and v)
    return bool(notes) and all(k in notes for k in other_keys)


def _is_variant_pair(a: str, b: str) -> bool:
    """True for two different regional variants of the same language, e.g. en-US and en-GB."""
    pa, pb = a.split("-"), b.split("-")
    return a.lower() != b.lower() and len(pa) > 1 and len(pb) > 1 and pa[0].lower() == pb[0].lower()


def validate(v: Vocabulary) -> list[Finding]:
    F: list[Finding] = []
    concepts = v.concepts
    LF, DF = v.label_field, v.def_field   # main-language label / definition
    if v.version == "v8":
        homonyms = cross_language_homonyms(concepts, LF)
        uris = Counter(c.get("uri") for c in concepts if c.get("uri"))
        for c in concepts:
            u = c.get("uri")
            if not u:
                F.append(_f("VT-URI-MISSING", c))
                continue
            name = u.strip()
            if not LOCAL_NAME_RE.match(name):
                F.append(_f("VT-URI-FORMAT", c, u))
            elif c.get(LF) and name != expected_name(c, LF, v.main_lang, homonyms):
                F.append(_f("VT-URI-LABEL", c, f"{name} vs {expected_name(c, LF, v.main_lang, homonyms)}"))
            if uris[u] > 1:
                F.append(_f("VT-URI-DUPLICATE", c, u))
    keys = Counter(c.key for c in concepts)
    by_key = v.by_key()
    id_re = re.compile(rf"^{re.escape(v.kortnavn)}-\d{{4}}$") if (v.version == "v8" and v.kortnavn) else None
    any_id_re = re.compile(r"^[A-Za-z0-9]{1,4}-\d{4}$")

    for c in concepts:
        if keys[c.key] > 1:
            F.append(_f("VT-ID-DUPLICATE", c, c.key))
        if id_re and not id_re.match(c.key):
            F.append(_f("VT-ID-FORMAT", c, c.key))
        if not c.get(LF):
            F.append(_f("VT-REQ-LABEL", c))
        if not c.get(DF):
            F.append(_f("VT-REQ-DEF", c))
        if v.main_lang == "nb" and (not c.get("label_nn") or not c.get("def_nn")):
            F.append(_f("VT-NN-MISSING", c))
        if not c.tier:
            F.append(_f("VT-TIER-EMPTY", c))
        elif c.tier not in TIERS:
            F.append(_f("VT-TIER-INVALID", c, repr(c.tier)))
        raw_st = (c.get("status") or "").strip()
        st = raw_st.lower()
        lit = re.fullmatch(r'"([^"]*)"@\w+', raw_st)
        if lit:
            F.append(_f("VT-STATUS-LITERAL", c, raw_st))
        elif st and st not in STATUS_VALUES:
            F.append(_f("VT-STATUS", c, st))
        if not c.get("contact_point"):
            F.append(_f("VT-CONTACT", c))
        lab = c.get(LF) or ""
        first_tok = re.split(r"[\s\-/]", lab, maxsplit=1)[0] if lab else ""
        if lab and lab[0].isupper() and not (first_tok.isupper() or any(ch.isdigit() for ch in first_tok)):
            F.append(_f("VT-LABEL-CASE", c, lab))
        for fld, prop in RELATION_FIELDS.items():
            for t in c.relations.get(fld, []):
                if t == c.key:
                    F.append(_f("VT-REF-SELF", c, prop))
                elif v.version == "v8" and not any_id_re.match(t):
                    F.append(_f("VT-REF-FORMAT", c, f"{prop} = {t!r}"))
                elif t not in by_key:
                    F.append(_f("VT-REF-DANGLING", c, f"{prop} -> {t}"))

    labels = Counter((c.get(LF) or "").strip().lower() for c in concepts if c.get(LF))
    for c in concepts:
        lab = (c.get(LF) or "").strip().lower()
        if lab and labels[lab] > 1:
            others = {o.key for o in concepts if o.key != c.key and (o.get(LF) or "").strip().lower() == lab}
            F.append(_f("VT-LABEL-NOTED" if _noted(c, others) else "VT-LABEL-DUPLICATE", c, lab))

    # homonyms across all label columns and languages (e.g. US "double crochet" vs UK "double crochet")
    uses = defaultdict(set)   # term -> {(concept key, field, tag)}
    for c in concepts:
        for fld, tag in label_fields(c.fields).items():
            vals = split_multi(c.get(fld)) if fld.startswith("alt_") else [c.get(fld)] if c.get(fld) else []
            for val in vals:
                uses[val.strip().lower()].add((c.key, fld, tag))
    for term, occ in uses.items():
        keys = {k for k, _, _ in occ}
        if len(keys) < 2 or all(f == LF for _, f, _ in occ):
            continue   # nb prefLabel duplicates are VT-LABEL-DUPLICATE
        for c_key in sorted(keys):
            mine_t = {t for k, _, t in occ if k == c_key}
            other_t = {(k, t) for k, _, t in occ if k != c_key}
            mine = sorted({f"{'alt' if f.startswith('alt_') else 'pref'}@{t}" for k, f, t in occ if k == c_key})
            others = sorted({f"{k} ({'alt' if f.startswith('alt_') else 'pref'}@{t})" for k, f, t in occ if k != c_key})
            # regional variants of one language (en-US / en-GB): the clash is the documented difference -> info
            variant = all(_is_variant_pair(a, b) for a in mine_t for _, b in other_t)
            rule = ("VT-LABEL-NOTED" if _noted(by_key[c_key], {k for k, _ in other_t})
                    else "VT-LABEL-VARIANT" if variant else "VT-LABEL-HOMONYM")
            F.append(_f(rule, by_key[c_key], f"'{term}' as {', '.join(mine)}; also {', '.join(others)}"))

    broader = {c.key: [t for t in c.relations["broader"] if t in by_key] for c in concepts}
    partof = {c.key: [t for t in c.relations["is_part_of"] if t in by_key] for c in concepts}
    for cyc in _find_cycles(broader):
        F.append(Finding("VT-CYCLE-BROADER", "error", cyc[0], by_key[cyc[0]].sheet, by_key[cyc[0]].row,
                         RULES["VT-CYCLE-BROADER"][1] + ": " + " -> ".join(cyc), "SKOS"))
    for cyc in _find_cycles(partof):
        F.append(Finding("VT-CYCLE-PARTOF", "error", cyc[0], by_key[cyc[0]].sheet, by_key[cyc[0]].row,
                         RULES["VT-CYCLE-PARTOF"][1] + ": " + " -> ".join(cyc), ""))

    narrower_count = Counter(t for ts in broader.values() for t in ts)
    for c in concepts:
        anc = _ancestors(broader, c.key)
        for t in c.relations["related"]:
            if t in anc or c.key in _ancestors(broader, t):
                F.append(_f("VT-RELATED-CLASH", c, t))

    linked = set()
    for c in concepts:
        for fld in RELATION_FIELDS:
            for t in c.relations[fld]:
                if t in by_key:
                    linked.add(c.key)
                    linked.add(t)
    for c in concepts:
        if c.tier == "1":
            if c.key not in linked:
                F.append(_f("VT-T1-ISOLATED", c, c.get(LF) or ""))
            for t in broader[c.key]:
                if by_key[t].tier != "1":
                    F.append(_f("VT-T1-BROADER-NON-T1", c, f"{t} (tier {by_key[t].tier})"))
        lab = (c.get(LF) or "").lower()
        n_parts = lab.count(",") + lab.count(" og ") + lab.count(" eller ")
        if n_parts >= 1 and " og " in lab and narrower_count[c.key] >= 2:
            F.append(_f("VT-LABEL-GROUPING", c, f"{c.get(LF)} ({narrower_count[c.key]} narrower)"))
    return F


def summarise(findings: list[Finding]) -> dict:
    by_rule = Counter((f.severity, f.rule) for f in findings)
    return {
        "errors": sum(1 for f in findings if f.severity == "error"),
        "warnings": sum(1 for f in findings if f.severity == "warning"),
        "info": sum(1 for f in findings if f.severity == "info"),
        "by_rule": [{"severity": s, "rule": r, "count": n, "description": RULES[r][1]}
                    for (s, r), n in sorted(by_rule.items(), key=lambda x: ("ewi".index(x[0][0][0]), x[0][1]))],
    }

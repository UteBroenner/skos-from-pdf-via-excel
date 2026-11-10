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
from .uri import LOCAL_NAME_RE, expected_name
from .samling import collections, sentence_problems

STATUS_VALUES = {"kandidat", "gjeldende", "utdatert", "forkastet"}
TIERS = {"1", "2", "3"}
PREFIX_RE = re.compile(r"(?<![\w-])vok:(?=[A-Za-z0-9])")
KODE_RE = re.compile(r"(?<![\w-])kode:(?=[A-Za-z0-9])")     # code-list references: kept until code lists are decided


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
    "VT-ID-FORMAT": ("error", "column A must be <kortnavn>-<concept name> (formula in the template)", "template v8 col A"),
    "VT-KORTNAVN": ("error", "kortnavn may only contain letters, digits and hyphens, starting with a letter or digit", "template v8"),
    "VT-ID-DUPLICATE": ("error", "ID used on more than one row", ""),
    "VT-URI-MISSING": ("error", "concept name for the URI (column B) missing; run `vocabtool uri` to generate it from the term", "S03"),
    "VT-URI-FORMAT": ("error", "column B must hold only the CamelCase concept name (letters and digits), e.g. Rekkverk", "S03"),
    "VT-URI-DUPLICATE": ("error", "concept name in column B used on more than one row, so two concepts get the same URI", ""),
    "VT-URI-LABEL": ("info", "concept name in column B differs from the CamelCase form of the main-language term (fine if chosen on purpose)", "S03"),
    "VT-REQ-LABEL": ("error", "prefLabel in the main language missing", ""),
    "VT-REQ-DEF": ("error", "definition in the main language missing", ""),
    "VT-REQ-DEF-CODE": ("warning", "code entry (has skos:notation) without a definition in the main language; code-table entries often have none in the source", ""),
    "VT-DEF-DERIVED": ("info", "definition derived from the code table, not quoted from the source ([avledet] in the editorial note); check it", ""),
    "VT-REF-FORMAT": ("error", "relation value is not a concept name (v8 relations use the names in column B)", ""),
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
    "VT-PREFIX": ("error", "no vok: prefix in the Excel table; write the concept name only (vok:Rekkverk -> Rekkverk)", "template v8"),
    "VT-PREFIX-KODE": ("info", "kode: reference to a code list; kept until the handling of code lists is decided", ""),
    "VT-COLL-MEMBERS": ("info", "collection recorded in scope notes (\"Inngår i samlingen …\"), with its members", ""),
    "VT-COLL-SINGLE": ("warning", "collection has only one member; check the spelling of the name", ""),
    "VT-COLL-SIMILAR": ("warning", "two collection names are almost the same; possibly a typo", ""),
    "VT-COLL-SPELLING": ("warning", "one collection written in more than one way; the first spelling becomes the label", ""),
    "VT-COLL-CONCEPT": ("info", "collection has the same name as a concept; if that row is only a heading, set its status to forkastet", ""),
    "VT-COLL-SYNTAX": ("warning", "main-language scope note mentions a collection but not as \"Inngår i samlingen X.\" or \"Inngår i samlingene X, Y.\"", ""),
    "VT-COLL-FORM": ("info", "use \"samlingen\" for one collection and \"samlingene\" for several", ""),
    "VT-COLL-OTHER-LANG": ("warning", "collection sentence in a scope note that is not in the main language; only the main-language note is read", ""),
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
        uris = Counter(c.get("uri") for c in concepts if c.get("uri"))
        for c in concepts:
            u = c.get("uri")
            if not u:
                F.append(_f("VT-URI-MISSING", c))
                continue
            name = u.strip()
            if not LOCAL_NAME_RE.match(name):
                F.append(_f("VT-URI-FORMAT", c, u))
            elif c.get(LF) and name != expected_name(c, LF):
                F.append(_f("VT-URI-LABEL", c, f"{name} vs {expected_name(c, LF)}"))
            if uris[u] > 1:
                F.append(_f("VT-URI-DUPLICATE", c, u))
    keys = Counter(c.key for c in concepts)
    by_key = v.by_key()
    if v.version == "v8" and not v.kortnavn:
        F.append(Finding("VT-KORTNAVN", "error", None, None, None, "kortnavn (short name of the vocabulary) is empty", "template v8"))
    elif v.version == "v8" and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", v.kortnavn):
        F.append(Finding("VT-KORTNAVN", "error", None, None, None, RULES["VT-KORTNAVN"][1] + f": {v.kortnavn}", "template v8"))

    for c in concepts:
        if keys[c.key] > 1 and v.version != "v8":        # v8: duplicate names are VT-URI-DUPLICATE
            F.append(_f("VT-ID-DUPLICATE", c, c.key))
        if v.version == "v8" and v.kortnavn and c.get("uri") and c.get("identifier") != f"{v.kortnavn}-{c.get('uri').strip()}":
            F.append(_f("VT-ID-FORMAT", c, f"{c.get('identifier')} (expected {v.kortnavn}-{c.get('uri').strip()})"))
        if v.version == "v8":
            for fld, val in c.fields.items():
                if isinstance(val, str) and PREFIX_RE.search(val):
                    F.append(_f("VT-PREFIX", c, f"{fld} = {val[:80]!r}"))
                if isinstance(val, str) and KODE_RE.search(val):
                    F.append(_f("VT-PREFIX-KODE", c, f"{fld}: {', '.join(sorted(set(re.findall(r'kode:[\w-]+', val))))}"))
        if not c.get(LF):
            F.append(_f("VT-REQ-LABEL", c))
        if not c.get(DF):
            F.append(_f("VT-REQ-DEF-CODE" if c.get("notation") else "VT-REQ-DEF", c))
        elif "[avledet]" in (c.get("editorial_note") or ""):
            F.append(_f("VT-DEF-DERIVED", c))
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
                elif v.version == "v8" and not LOCAL_NAME_RE.match(t):
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
    F += _collection_findings(v, by_key)
    return F


def _collection_findings(v: Vocabulary, by_key) -> list[Finding]:
    """Collections from the scope-note sentence (see samling.py)."""
    import difflib
    F = [_f(rule, c, detail) for c, rule, detail in sentence_problems(v)]
    cols = collections(v)
    names = {(c.get("uri") or "").strip() for c in v.concepts}
    def coll(rule, col, extra):
        first = by_key[col.members[0]]
        return Finding(rule, RULES[rule][0], first.key, first.sheet, first.row,
                       f"{RULES[rule][1]}: {extra}", RULES[rule][2])
    for col in cols.values():
        F.append(coll("VT-COLL-MEMBERS", col, f"{col.label} ({len(col.members)}): {'; '.join(col.members)}"))
        if len(col.members) == 1:
            F.append(coll("VT-COLL-SINGLE", col, col.label))
        if len(col.spellings) > 1:
            F.append(coll("VT-COLL-SPELLING", col, " / ".join(sorted(col.spellings))))
        if col.name in names:
            F.append(coll("VT-COLL-CONCEPT", col, col.name))
    keys = sorted(cols)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() >= 0.9:
                F.append(coll("VT-COLL-SIMILAR", cols[a], f"{cols[a].label} / {cols[b].label}"))
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

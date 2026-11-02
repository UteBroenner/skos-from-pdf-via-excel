"""Read SKOS vocabulary workbooks (template v7 and v8) into plain records.

Code lists (the `kodeverk` sheet) are deliberately ignored.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import openpyxl

# Normalised header (property) -> canonical field name.
# Headers are normalised by removing whitespace and any "(separator=...)" suffix.
PROPERTY_MAP = {
    "URI": "uri",                       # v7: prefixed name (vok:X) is the row key; v8: formula
    "dct:identifier": "identifier",     # v8: row key (kortnavn-0001); v7: usually empty
    "skos:prefLabel@nb": "label_nb",
    "skos:prefLabel@en": "label_en",
    "skos:prefLabel@nn": "label_nn",
    "skos:notation": "notation",
    "skos:definition@nb": "def_nb",
    "skos:definition@en": "def_en",
    "skos:definition@nn": "def_nn",
    "skos:altLabel@nb": "alt_nb",
    "skos:altLabel@en": "alt_en",
    "skos:altLabel@nn": "alt_nn",
    "dct:audience": "audience",
    "dct:source": "source",
    "skosno:relationshipWithSource": "relationship_with_source",
    "skos:scopeNote@nb": "scope_note",
    "skos:editorialNote": "editorial_note",
    "skos:example": "example",
    "dct:subject": "subject",
    "skos:hiddenLabel@nb": "hidden_nb",
    "skos:broader": "broader",
    "xkos:isPartOf": "is_part_of",
    "skos:related": "related",
    "skosno:relationRole": "relation_role",
    "skos:exactMatch": "exact_match",
    "skos:closeMatch": "close_match",
    "dcat:contactPoint": "contact_point",
    "dct:created": "created",
    "dct:modified": "modified",
    "owl:versionInfo": "version_info",
    "adms:versionNotes": "version_notes",
    "skos:changeNote": "change_note",   # v7 only
    "euvoc:status": "status",
    "euvoc:startDate": "start_date",
    "euvoc:endDate": "end_date",
    "skosno:dataStructureLabel": "data_structure_label",
    "skosno:valueRange": "value_range",
    "tier": "tier",
}
# dct:contributor appears twice in v8 (created by / modified by), once in v7.
CONTRIBUTOR_FIELDS = ["created_by", "modified_by"]

RELATION_FIELDS = {"broader": "skos:broader", "is_part_of": "xkos:isPartOf", "related": "skos:related"}
EXCLUDED_SHEETS = {"kodeverk", "lister"}


def normalise_header(value) -> str:
    s = re.sub(r"\s+", "", str(value or ""))
    return s.split("(")[0]


def split_multi(value) -> list[str]:
    if value is None:
        return []
    return [p.strip() for p in re.split(r"[,;\n]", str(value)) if p.strip()]


def as_text(value):
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
    s = str(value).strip()
    return s or None


@dataclass
class Concept:
    key: str                 # ID used for relations (v8: dct:identifier, v7: prefixed URI)
    sheet: str
    row: int
    fields: dict = field(default_factory=dict)
    relations: dict = field(default_factory=dict)   # field -> list of target keys

    def get(self, name, default=None):
        return self.fields.get(name, default)

    @property
    def tier(self) -> str | None:
        t = self.fields.get("tier")
        if t is None:
            return None
        t = str(t).strip()
        return t[:-2] if t.endswith(".0") else t


@dataclass
class Vocabulary:
    path: Path
    version: str             # "v8" or "v7"
    kortnavn: str | None
    title: str | None
    scheme_uri: str | None
    concepts: list[Concept]
    columns: dict            # sheet -> {canonical field: column letter}
    unmapped_headers: dict   # sheet -> [header]

    def by_key(self) -> dict[str, Concept]:
        return {c.key: c for c in self.concepts}


def _find_header_row(ws, max_scan=40):
    for r in range(1, min(ws.max_row, max_scan) + 1):
        vals = [normalise_header(c.value) for c in ws[r]]
        if "skos:prefLabel@nb" in vals:
            return r, vals
    return None, None


def _scheme_meta(ws):
    meta = {}
    for r in range(1, 20):
        a = normalise_header(ws.cell(r, 1).value)
        b = ws.cell(r, 2).value
        if a == "ConceptSchemeURI":
            meta["scheme_uri"] = b
        elif a.startswith("kortnavn"):
            meta["kortnavn"] = as_text(b)
        elif a == "dct:title":
            meta["title"] = as_text(b)
    return meta


def read_workbook(path: str | Path) -> Vocabulary:
    path = Path(path)
    wb = openpyxl.load_workbook(path, data_only=True)
    concepts: list[Concept] = []
    columns, unmapped = {}, {}
    version, meta = None, {}

    for ws in wb.worksheets:
        if ws.title.strip().lower() in EXCLUDED_SHEETS:
            continue
        hdr_row, headers = _find_header_row(ws)
        if hdr_row is None:
            continue
        # v8 has a second header row with technical names (intern_identifikator, ...)
        next_row = [normalise_header(c.value) for c in ws[hdr_row + 1]]
        is_v8 = "intern_identifikator" in next_row or headers[0] == "dct:identifier"
        version = version or ("v8" if is_v8 else "v7")
        first_data = hdr_row + 2 if "intern_identifikator" in next_row else hdr_row + 1
        if not meta:
            meta = _scheme_meta(ws)

        colmap, skipped, contrib = {}, [], 0
        for idx, h in enumerate(headers):
            if not h:
                continue
            if h == "dct:contributor":
                if contrib < len(CONTRIBUTOR_FIELDS):
                    colmap[CONTRIBUTOR_FIELDS[contrib]] = idx
                contrib += 1
            elif h in PROPERTY_MAP:
                colmap.setdefault(PROPERTY_MAP[h], idx)
            else:
                skipped.append(h)
        columns[ws.title] = {k: openpyxl.utils.get_column_letter(i + 1) for k, i in colmap.items()}
        unmapped[ws.title] = skipped

        key_field = "identifier" if is_v8 else "uri"
        for r_idx, row in enumerate(ws.iter_rows(min_row=first_data, values_only=True), start=first_data):
            rec = {k: as_text(row[i]) if i < len(row) else None for k, i in colmap.items()}
            if not any(rec.get(k) for k in ("identifier", "uri", "label_nb")):
                continue
            key = rec.get(key_field) or rec.get("uri") or rec.get("identifier") or f"{ws.title}!row{r_idx}"
            rels = {f: split_multi(rec.get(f)) for f in RELATION_FIELDS}
            concepts.append(Concept(key=key.strip(), sheet=ws.title, row=r_idx, fields=rec, relations=rels))

    kortnavn = meta.get("kortnavn")
    if kortnavn and kortnavn.startswith("<"):
        kortnavn = None
    if not kortnavn and meta.get("scheme_uri") and not str(meta["scheme_uri"]).startswith("="):
        kortnavn = str(meta["scheme_uri"]).rstrip("/").rsplit("/", 1)[-1]
    return Vocabulary(path=path, version=version or "unknown", kortnavn=kortnavn,
                      title=meta.get("title"), scheme_uri=as_text(meta.get("scheme_uri")),
                      concepts=concepts, columns=columns, unmapped_headers=unmapped)

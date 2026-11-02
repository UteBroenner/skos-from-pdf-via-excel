"""Excel (v8) -> LinkML data (YAML) -> RDF Turtle, plus SHACL validation.

The LinkML schema (schema/svv_vokabular.yaml) is the single source of truth.
This module adds what the standard LinkML tooling (1.12) does not do:

* RDF writer that applies per-slot ``in_language`` tags and writes enum
  ``meaning`` URIs (the stock rdflib dumper writes plain literals);
* SHACL post-processing: for slots that share one property (skos:prefLabel @nb/@en/@nn,
  dct:contributor), the generated property shapes each carry sh:maxCount 1 on the
  same path, which rejects valid data. They are replaced by qualified shapes per language.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import RDF, XSD, SH

from linkml_runtime.utils.schemaview import SchemaView

from .reader import Vocabulary, read_workbook, split_multi

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema" / "svv_vokabular.yaml"
CROSS_ROW_SHAPES = ROOT / "schema" / "shapes" / "cross_row.shacl.ttl"

# reader field -> schema slot
FIELD_TO_SLOT = {
    "identifier": "identifier", "label_nb": "pref_label_nb", "label_en": "pref_label_en", "label_nn": "pref_label_nn",
    "notation": "notation", "def_nb": "definition_nb", "def_en": "definition_en", "def_nn": "definition_nn",
    "alt_nb": "alt_label_nb", "alt_en": "alt_label_en", "alt_nn": "alt_label_nn", "audience": "audience",
    "source": "source", "relationship_with_source": "relationship_with_source", "scope_note": "scope_note",
    "editorial_note": "editorial_note", "example": "example", "subject": "subject", "hidden_nb": "hidden_label",
    "broader": "broader", "is_part_of": "is_part_of", "related": "related", "relation_role": "relation_role",
    "exact_match": "exact_match", "close_match": "close_match", "contact_point": "contact_point",
    "created": "created", "created_by": "created_by", "modified": "modified", "modified_by": "modified_by",
    "version_info": "version_info", "version_notes": "version_notes", "status": "status",
    "start_date": "start_date", "end_date": "end_date", "data_structure_label": "data_structure_label",
    "value_range": "value_range", "tier": "tier",
}
RELATION_SLOTS = {"broader", "is_part_of", "related"}
BASE = "http://example.org/vegvesen/vokabular/"


def schemaview() -> SchemaView:
    return SchemaView(str(SCHEMA))


# ---------------------------------------------------------------- Excel -> data
def workbook_to_data(v: Vocabulary, sv: SchemaView | None = None) -> dict:
    """Build a LinkML instance (dict) of ConceptScheme from a v8 workbook."""
    sv = sv or schemaview()
    if v.version != "v8":
        raise ValueError("LinkML conversion expects a v8 workbook (relations as IDs); migrate v7 first")
    scheme_uri = f"{BASE}{v.kortnavn}"
    id_to_uri = {c.key: f"{scheme_uri}/{c.key}" for c in v.concepts}
    concepts = []
    for c in v.concepts:
        rec = {"uri": id_to_uri[c.key], "in_scheme": scheme_uri}
        for f, slot_name in FIELD_TO_SLOT.items():
            val = c.get(f)
            if val is None:
                continue
            slot = sv.get_slot(slot_name)
            if slot_name in RELATION_SLOTS:
                # unknown IDs still become URIs, so SHACL reports them (target is not a skos:Concept)
                val = [id_to_uri.get(t, f"{scheme_uri}/{t}") for t in c.relations[f]]
            elif slot.multivalued:
                val = split_multi(val)
            elif slot.range == "integer":
                try:
                    val = int(float(val))
                except ValueError:
                    pass
            elif slot_name == "status":
                val = val.strip().strip('"').split('"@')[0].lower()
            if val in ([], ""):
                continue
            rec[slot_name] = val
        concepts.append(rec)
    return {"uri": scheme_uri, "kortnavn": v.kortnavn, "title": v.title, "concepts": concepts}


# ---------------------------------------------------------------- data -> RDF
IRI_RE = __import__("re").compile(r"^(https?|urn):[^\s<>\"{}|\\^`]+$")


def data_to_graph(data: dict, sv: SchemaView | None = None, skipped: list | None = None) -> Graph:
    """Write RDF. Values that cannot be IRIs (for a uri/Concept range) are not written
    but appended to ``skipped`` as (subject, slot, value)."""
    sv = sv or schemaview()
    skipped = skipped if skipped is not None else []
    g = Graph()
    for p, ns in sv.schema.prefixes.items():
        g.bind(p, Namespace(ns.prefix_reference))
    g.bind("vokdata", Namespace(data["uri"] + "/"))

    def emit(subject: URIRef, cls: str, obj: dict):
        g.add((subject, RDF.type, URIRef(sv.get_uri(sv.get_class(cls), expand=True))))
        for slot_name, value in obj.items():
            slot = sv.induced_slot(slot_name, cls)
            if slot.identifier or (slot.annotations and "rdf_skip" in slot.annotations):
                continue
            pred = URIRef(sv.get_uri(slot, expand=True))
            for v in (value if isinstance(value, list) else [value]):
                node = to_node(slot, v)
                if node is None:
                    skipped.append((str(subject), slot.name, str(v)))
                else:
                    g.add((subject, pred, node))

    def to_node(slot, v):
        rng = slot.range
        if rng in sv.all_classes() or rng in ("uri", "uriorcurie"):
            return URIRef(str(v)) if IRI_RE.match(str(v)) else None
        if rng in sv.all_enums():
            pv = sv.get_enum(rng).permissible_values.get(str(v))
            if pv is not None and pv.meaning:
                return URIRef(sv.expand_curie(pv.meaning))
            return Literal(str(v))
        if rng == "date":
            return Literal(str(v)[:10], datatype=XSD.date)
        if rng == "integer":
            return Literal(int(v), datatype=XSD.integer)
        return Literal(str(v), lang=slot.in_language) if slot.in_language else Literal(str(v))

    scheme = URIRef(data["uri"])
    emit(scheme, "ConceptScheme", {k: v for k, v in data.items() if k not in ("uri", "concepts")})
    for c in data.get("concepts", []):
        emit(URIRef(c["uri"]), "Concept", {k: v for k, v in c.items() if k != "uri"})
    return g


# ---------------------------------------------------------------- SHACL
def build_shapes(generated_shacl: str | Path, sv: SchemaView | None = None) -> Graph:
    """Generated SHACL with language-/role-specific slots fixed, plus cross-row shapes."""
    sv = sv or schemaview()
    g = Graph().parse(str(generated_shacl), format="turtle")
    by_path: dict[URIRef, list] = {}
    for s in sv.all_slots().values():
        if s.slot_uri:
            by_path.setdefault(URIRef(sv.expand_curie(s.slot_uri)), []).append(s)
    shared = {p: ss for p, ss in by_path.items() if len(ss) > 1}

    for node_shape in set(g.subjects(RDF.type, SH.NodeShape)):
        cls_name = str(node_shape).rsplit("/", 1)[-1].rsplit("#", 1)[-1]
        if cls_name not in sv.all_classes():
            continue
        class_slots = set(sv.class_slots(cls_name))
        for prop in list(g.objects(node_shape, SH.property)):
            path = g.value(prop, SH.path)
            if path not in shared:
                continue
            g.remove((node_shape, SH.property, prop))
            for t in list(g.triples((prop, None, None))):
                g.remove(t)
        for path, slots in shared.items():
            slots = [s for s in slots if s.name in class_slots]
            if not slots:
                continue
            langs = [s.in_language for s in slots if s.in_language]
            for s in slots:
                p = BNode()
                g.add((node_shape, SH.property, p))
                g.add((p, SH.path, path))
                g.add((p, SH.name, Literal(s.name)))
                if s.in_language and s.multivalued and not s.required:
                    continue   # no count to qualify; the shared sh:languageIn shape below covers it
                if s.in_language:
                    q = BNode()
                    lst = BNode()
                    Collection(g, lst, [Literal(s.in_language)])
                    g.add((q, SH.languageIn, lst))
                    g.add((p, SH.qualifiedValueShape, q))
                    if not s.multivalued:
                        g.add((p, SH.qualifiedMaxCount, Literal(1)))
                    if s.required:
                        g.add((p, SH.qualifiedMinCount, Literal(1)))
                    if s.pattern:
                        g.add((q, SH.pattern, Literal(s.pattern)))
                else:
                    if s.pattern:
                        g.add((p, SH.pattern, Literal(s.pattern)))
            if langs and len(langs) == len(slots):
                # every value on this path must carry one of the modelled languages
                p = BNode()
                lst = BNode()
                Collection(g, lst, [Literal(x) for x in langs])
                g.add((node_shape, SH.property, p))
                g.add((p, SH.path, path))
                g.add((p, SH.languageIn, lst))
            elif not langs:
                # same property used for several roles (e.g. dct:contributor created_by / modified_by)
                p = BNode()
                g.add((node_shape, SH.property, p))
                g.add((p, SH.path, path))
                g.add((p, SH.maxCount, Literal(len(slots))))
    # language-tagged single slots: LinkML emits sh:datatype xsd:string, which rejects "..."@nb
    lang_paths = {URIRef(sv.expand_curie(s.slot_uri)): s.in_language for s in sv.all_slots().values()
                  if s.slot_uri and s.in_language and URIRef(sv.expand_curie(s.slot_uri)) not in shared}
    for prop in set(g.subjects(SH.path, None)):
        path = g.value(prop, SH.path)
        if path in lang_paths and (prop, SH.datatype, XSD.string) in g:
            g.remove((prop, SH.datatype, XSD.string))
            g.add((prop, SH.datatype, RDF.langString))
            lst = BNode()
            Collection(g, lst, [Literal(lang_paths[path])])
            g.add((prop, SH.languageIn, lst))
    if CROSS_ROW_SHAPES.exists():
        g.parse(str(CROSS_ROW_SHAPES), format="turtle")
    return g


def shacl_validate(data_graph: Graph, shapes: Graph):
    from pyshacl import validate
    conforms, report_graph, report_text = validate(data_graph, shacl_graph=shapes, inference="none",
                                                   advanced=True, allow_warnings=True)
    results = []
    for r in report_graph.subjects(RDF.type, SH.ValidationResult):
        results.append({
            "severity": str(report_graph.value(r, SH.resultSeverity)).rsplit("#", 1)[-1],
            "focus": str(report_graph.value(r, SH.focusNode)),
            "path": str(report_graph.value(r, SH.resultPath) or ""),
            "value": str(report_graph.value(r, SH.value) or ""),
            "component": str(report_graph.value(r, SH.sourceConstraintComponent)).rsplit("#", 1)[-1],
            "message": str(report_graph.value(r, SH.resultMessage) or ""),
        })
    return conforms, results


def write_yaml(data: dict, path: str | Path):
    Path(path).write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")

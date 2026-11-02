#!/usr/bin/env bash
# Regenerate artefacts from the LinkML schema. Run from the repository root.
set -euo pipefail
V=.venv/bin
S=schema/svv_vokabular.yaml
O=schema/generated
mkdir -p "$O" "$O/docs"
$V/gen-pydantic "$S"     > "$O/svv_vokabular_pydantic.py"
$V/gen-json-schema "$S"  > "$O/svv_vokabular.schema.json"
$V/gen-shacl "$S"        > "$O/svv_vokabular.shacl.ttl"
$V/gen-owl "$S" 2>/dev/null > "$O/svv_vokabular.owl.ttl"
$V/gen-doc "$S" -d "$O/docs" >/dev/null 2>&1
# SHACL with the project fixes (language slots, langString) and cross-row rules
$V/python -c "from vocabtool.linkml_rdf import build_shapes; build_shapes('$O/svv_vokabular.shacl.ttl').serialize('$O/svv_vokabular.shacl.fixed.ttl', format='turtle')"
echo "generated: $(ls $O | tr '\n' ' ')"

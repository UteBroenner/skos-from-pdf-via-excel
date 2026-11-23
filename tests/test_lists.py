"""The value lists (vocabtool/lists.py) must match the schema enums, and survive a save by the tools.

Run: .venv/bin/python -m pytest tests  (or .venv/bin/python tests/test_lists.py)
"""
from pathlib import Path
import sys
import tempfile

import openpyxl
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vocabtool.lists import LISTS, save_workbook          # noqa: E402
from vocabtool.reader import audience, source_relation    # noqa: E402

SCHEMA = yaml.safe_load((ROOT / "schema/svv_vokabular.yaml").read_text(encoding="utf-8"))


def _expand(curie):
    prefix, local = curie.split(":", 1)
    return SCHEMA["prefixes"][prefix] + local


def test_lists_match_schema():
    enums = SCHEMA["enums"]
    by_prop = {prop: rows for prop, _, _, _, rows in LISTS}
    status = {k: _expand(v["meaning"]) for k, v in enums["ConceptStatus"]["permissible_values"].items()}
    assert status == {label: uri for label, _, uri in by_prop["euvoc:status"]}
    aud = {k: _expand(v["meaning"]) for k, v in enums["Audience"]["permissible_values"].items()}
    assert aud == {code: uri for _, code, uri in by_prop["dct:audience"]}
    assert all(audience(label) == code for label, code, _ in by_prop["dct:audience"])
    rel = {k: _expand(v["meaning"]) for k, v in enums["RelationshipWithSource"]["permissible_values"].items()}
    assert rel == {code: uri for _, code, uri in by_prop["skosno:relationshipWithSource"]}
    assert all(source_relation(label) == code for label, code, _ in by_prop["skosno:relationshipWithSource"])


def test_dropdowns_survive_save():
    tpl = ROOT / "templates/SKOS-Excel-mal-v9-for-import.xlsx"
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "x.xlsx"
        for _ in range(2):                                   # save twice: nothing lost, nothing duplicated
            wb = openpyxl.load_workbook(out if out.exists() else tpl)
            save_workbook(wb, out)
        wb = openpyxl.load_workbook(out)
        dvs = {str(dv.sqref).split(":")[0][:-2]: dv.formula1 for dv in wb["vokabular"].data_validations.dataValidation}
        assert dvs == {"AI": '"kandidat,gjeldende,utdatert,forkastet"', "M": '"allmennheten,spesialist"',
                       "O": '"basert på kilde,egendefinert,sitat fra kilde"', "AO": '"1,2,3"'}
        assert wb["lister"].sheet_state == "hidden"


if __name__ == "__main__":
    test_lists_match_schema()
    test_dropdowns_survive_save()
    print("ok")

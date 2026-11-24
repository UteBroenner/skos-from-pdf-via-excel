"""The internal column 'type' (called 'tier' before 24 November 2026): both headers are read; tools write 'type'.

Run: .venv/bin/python -m pytest tests  (or .venv/bin/python tests/test_type.py)
"""
from pathlib import Path
import sys
import tempfile

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vocabtool.reader import read_workbook                  # noqa: E402
from vocabtool.template_ext import apply_formulas           # noqa: E402
from vocabtool.lists import save_workbook                   # noqa: E402


def _workbook(header, d):
    wb = openpyxl.load_workbook(ROOT / "templates/SKOS-Excel-mal-v9-for-import.xlsx")
    ws = wb["vokabular"]
    col = next(c.column for c in ws[23] if c.value == "type")
    ws.cell(23, col).value = header
    ws["B14"], ws["C25"], ws.cell(25, col).value = "T", "rekkverk", 2
    out = Path(d) / f"{header}.xlsx"
    wb.save(out)
    return out, col


def test_old_and_new_header():
    with tempfile.TemporaryDirectory() as d:
        for header in ("tier", "type"):
            path, col = _workbook(header, d)
            assert [c.type for c in read_workbook(path).concepts] == ["2"]
        wb = openpyxl.load_workbook(path.with_name("tier.xlsx"))
        apply_formulas(wb)                                   # tools rename the header
        save_workbook(wb, path)
        assert openpyxl.load_workbook(path)["vokabular"].cell(23, col).value == "type"


if __name__ == "__main__":
    test_old_and_new_header()
    print("ok")

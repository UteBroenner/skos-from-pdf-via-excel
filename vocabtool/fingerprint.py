"""Row fingerprint for change detection in the Power Automate import.

SHA-256 (hex) over "technical_name=value" lines, sorted by technical name, for every column
inside the Excel table except the ID, the governance columns and the fingerprint itself.
Independent of column order. Values are normalised: text stripped, dates yyyy-mm-dd,
whole numbers without decimals, empty = "".

The same rule must be used wherever the fingerprint is (re)computed, e.g. in an Office Script.
"""
from __future__ import annotations

import hashlib
from datetime import date, datetime

EXCLUDED = {"intern_identifikator", "dato_opprettet", "opprettet_av", "dato_sist_endret", "sist_endret_av",
            "endringshash", "tier"}


def normalise(value) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def fingerprint(row_values: dict) -> str:
    """row_values: {technical name: cell value}."""
    lines = [f"{k}={normalise(v)}" for k, v in sorted(row_values.items()) if k and k not in EXCLUDED]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def row_values(ws, row: int, tech_row: int, last_col: int) -> dict:
    return {ws.cell(tech_row, c).value: ws.cell(row, c).value for c in range(1, last_col + 1)
            if ws.cell(tech_row, c).value}

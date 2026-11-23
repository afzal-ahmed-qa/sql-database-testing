"""Runs every check in checks/**.sql.

A check is a query that returns the rows that break a rule: no rows means the
rule holds. The header of each file gives its id, title and severity. A check
with "known_defect" documents a real defect in the data (docs/defects.md): it is
expected to find rows, and with xfail_strict it turns red the day it finds none,
so the defect list never goes out of date.
"""

import re
from pathlib import Path

import pytest

CHECKS = sorted((Path(__file__).resolve().parent.parent / "checks").rglob("*.sql"))


def header(sql: str) -> dict[str, str]:
    return dict(re.findall(r"^--\s*(\w+):\s*(.+)$", sql, flags=re.MULTILINE))


def params() -> list:
    cases = []
    for path in CHECKS:
        meta = header(path.read_text())
        marks = []
        if "known_defect" in meta:
            marks.append(pytest.mark.xfail(reason=f"{meta['known_defect']}: known defect, see docs/defects.md"))
        cases.append(pytest.param(path, meta, id=f"{meta['id']} {meta['title']}", marks=marks))
    return cases


@pytest.mark.parametrize(("path", "meta"), params())
def test_check(db, path, meta, record_property):
    cursor = db.execute(path.read_text())
    columns = [c.name for c in cursor.description]
    rows = cursor.fetchall()
    record_property("violations", len(rows))
    sample = "\n".join(str(dict(zip(columns, row))) for row in rows[:5])
    assert not rows, f"{meta['id']} ({meta['severity']}): {len(rows)} violating rows, e.g.\n{sample}"

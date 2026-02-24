from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_tests_import_from_bindings() -> None:
    offenders: list[str] = []
    for py in ROOT.rglob("*.py"):
        if ".venv" in py.parts:
            continue
        text = py.read_text(encoding="utf-8")
        if "tigrbl.bindings" in text:
            offenders.append(str(py.relative_to(ROOT)))

    assert offenders == [], (
        "Found legacy bindings imports; tests should use tigrbl.mapping or top-level "
        f"exports instead: {offenders}"
    )

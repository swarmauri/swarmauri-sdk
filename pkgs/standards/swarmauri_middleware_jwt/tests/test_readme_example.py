"""Tests for the README example."""

from __future__ import annotations

import pathlib
from typing import Dict

import pytest


README_PATH = pathlib.Path(__file__).resolve().parents[1] / "README.md"


def _extract_first_python_block() -> str:
    """Return the first Python code block from the README."""
    contents = README_PATH.read_text(encoding="utf-8")
    lines = []
    in_block = False

    for raw_line in contents.splitlines():
        stripped = raw_line.strip()
        if not in_block and stripped.startswith("```python"):
            in_block = True
            continue
        if in_block and stripped.startswith("```"):
            break
        if in_block:
            lines.append(raw_line)

    if not lines:
        raise AssertionError("README is missing a Python example block")

    return "\n".join(lines)


@pytest.mark.example
def test_readme_example_runs(capsys):
    """Execute the README example to ensure it stays up-to-date."""
    code = _extract_first_python_block()
    namespace: Dict[str, object] = {"__name__": "__main__"}
    exec(compile(code, str(README_PATH), "exec"), namespace)  # noqa: S102

    captured = capsys.readouterr()
    assert "demo-user" in captured.out

    run_example = namespace.get("run_example")
    assert callable(run_example), "README example must define run_example()"
    assert run_example() == {"subject": "demo-user"}

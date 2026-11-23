"""Ensure the README example continues to run successfully."""

from __future__ import annotations

from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parent.parent / "README.md"
EXAMPLE_START = "<!-- example-start -->"
EXAMPLE_END = "<!-- example-end -->"


def _extract_readme_example() -> str:
    text = README_PATH.read_text(encoding="utf-8")

    try:
        start = text.index(EXAMPLE_START) + len(EXAMPLE_START)
        end = text.index(EXAMPLE_END, start)
    except ValueError as exc:  # pragma: no cover - signals README drift
        raise AssertionError("README example markers are missing") from exc

    fenced = text[start:end]
    fence_start = fenced.index("```") + 3
    fence_end = fenced.rindex("```")
    code = fenced[fence_start:fence_end].lstrip()
    if code.startswith("python"):
        code = code[len("python") :].lstrip("\n")
    return code


@pytest.mark.example
def test_readme_example_executes() -> None:
    example = _extract_readme_example()
    exec(compile(example, str(README_PATH), "exec"), {})

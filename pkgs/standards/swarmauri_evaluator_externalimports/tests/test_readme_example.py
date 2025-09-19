"""Execute the README example to ensure it remains accurate."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest


README_PATH = Path(__file__).resolve().parent.parent / "README.md"


def _load_readme_example() -> str:
    """Extract the first Python code block from the README."""

    contents = README_PATH.read_text(encoding="utf-8")
    lines = contents.splitlines()

    code_lines = []
    in_block = False

    for line in lines:
        if not in_block and line.strip().startswith("```python"):
            in_block = True
            continue

        if in_block and line.strip().startswith("```"):
            break

        if in_block:
            code_lines.append(line)

    if not code_lines:
        raise AssertionError("README example code block was not found")

    return "\n".join(code_lines)


@pytest.mark.example
def test_readme_example_executes() -> None:
    """Run the README usage example and assert the documented behaviour."""

    namespace: Dict[str, Any] = {}
    code = _load_readme_example()
    exec(compile(code, str(README_PATH), "exec"), namespace)  # noqa: S102

    evaluate_example = namespace.get("evaluate_example")
    assert callable(evaluate_example), (
        "README example should expose an `evaluate_example` function"
    )

    score, details = evaluate_example()

    assert isinstance(score, float)
    assert score == pytest.approx(0.9)

    assert isinstance(details, dict)
    assert set(details["external_modules"]) == {"numpy"}
    assert details["external_imports_count"] == 1
    assert details["unique_external_modules"] == 1

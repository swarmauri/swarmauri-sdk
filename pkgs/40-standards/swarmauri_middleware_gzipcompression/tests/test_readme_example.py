"""Tests that ensure the README example stays runnable."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


@pytest.mark.example
def test_readme_example_executes() -> None:
    """Execute the Python example from the README to keep it in sync."""
    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    match = re.search(r"```python\s*(.*?)```", readme_text, re.DOTALL)
    assert match, "No python example found in README.md"

    example_code = match.group(1)
    namespace: dict[str, object] = {}
    exec(compile(example_code, str(readme_path), "exec"), namespace)

    run_example = namespace.get("run_example")
    assert callable(run_example), "README example must define run_example()"

    run_example()

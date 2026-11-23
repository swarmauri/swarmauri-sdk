from __future__ import annotations

import re
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


@pytest.mark.example
def test_readme_python_example_executes(capsys):
    """Execute the README example to ensure it remains up to date."""

    readme_text = README_PATH.read_text(encoding="utf-8")
    match = re.search(r"```python\n(?P<code>.*?)```", readme_text, re.DOTALL)
    assert match, "Python example not found in README.md"

    namespace: dict[str, object] = {}
    exec(compile(match.group("code"), str(README_PATH), "exec"), namespace)  # noqa: S102

    captured_lines = capsys.readouterr().out.strip().splitlines()
    assert len(captured_lines) == 2, captured_lines

    first_data = namespace["first_data"]
    second_data = namespace["second_data"]

    assert isinstance(first_data, dict)
    assert isinstance(second_data, dict)
    assert first_data["session_id"] == second_data["session_id"]
    assert first_data["visits"] == 1
    assert second_data["visits"] == 2
    assert captured_lines[0].strip() == str(first_data)
    assert captured_lines[1].strip() == str(second_data)

from __future__ import annotations

import re
from pathlib import Path

import pytest

README_PATH = Path(__file__).resolve().parents[2] / "README.md"
EXAMPLE_PATTERN = re.compile(r"## Example.*?```python\n(.*?)```", re.DOTALL)


@pytest.mark.example
def test_readme_example_runs(capsys: pytest.CaptureFixture[str]) -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    match = EXAMPLE_PATTERN.search(readme)
    assert match, "README example code block not found"

    snippet = match.group(1)
    capsys.readouterr()  # Clear any pre-existing captured output.

    exec(compile(snippet, README_PATH.name, "exec"), {})  # noqa: S102

    captured = capsys.readouterr()
    output_lines = [line for line in captured.out.splitlines() if line]
    assert output_lines, "README example produced no output"
    assert output_lines[-1] == "{'message': 'hello'}"

from __future__ import annotations

import re
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


def _extract_usage_snippet() -> str:
    text = README_PATH.read_text()
    match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
    if not match:
        raise AssertionError("Usage example not found in README.md")
    return match.group(1)


@pytest.mark.example
def test_readme_usage_example_runs(capsys):
    code = _extract_usage_snippet()
    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(code, namespace)
    captured = capsys.readouterr()
    assert "Loaded key:" in captured.out

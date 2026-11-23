from __future__ import annotations

import re
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


def _extract_readme_example() -> str:
    text = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(r"```python\n(.*?)\n```", re.DOTALL)
    for match in pattern.finditer(text):
        snippet = match.group(1)
        if "PasetoV4TokenService" in snippet:
            return snippet
    raise AssertionError("Unable to locate README example code block")


@pytest.mark.example
def test_readme_example_exec(capsys) -> None:
    code = _extract_readme_example()
    compiled = compile(code, str(README_PATH), "exec")
    globals_dict: dict[str, object] = {"__name__": "__main__"}
    exec(compiled, globals_dict)
    output = capsys.readouterr().out
    assert "Verified role: admin" in output
    assert "Local feature flag: beta" in output

from __future__ import annotations

import re
from pathlib import Path
from textwrap import dedent

import pytest

from .._helpers import patch_dummy_github

README_PATH = Path(__file__).resolve().parents[2] / "README.md"


def _readme_python_example() -> str:
    text = README_PATH.read_text(encoding="utf-8")
    match = re.search(r"```python\s+(.*?)```", text, re.DOTALL)
    if not match:
        msg = "Expected a Python example in README.md"
        raise AssertionError(msg)
    return dedent(match.group(1)).strip()


@pytest.mark.example
def test_readme_usage_example(monkeypatch):
    patch_dummy_github(monkeypatch)
    example = _readme_python_example()
    namespace: dict[str, object] = {"__name__": "__readme_example__"}
    exec(compile(example, str(README_PATH), "exec"), namespace)
    filt = namespace.get("filt")
    assert filt is not None, "README example should define `filt`"
    assert filt.root_uri == "ghrel://org/repo/tag/artifacts/"

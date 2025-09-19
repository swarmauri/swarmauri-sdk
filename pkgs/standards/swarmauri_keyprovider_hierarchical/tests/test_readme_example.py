"""Ensure the README quickstart snippet stays runnable."""

from __future__ import annotations

import contextlib
import io
import re
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


@pytest.mark.example
def test_readme_quickstart_example(tmp_path, monkeypatch):
    """Execute the README quickstart example as a regression test."""
    text = README_PATH.read_text(encoding="utf-8")
    start_marker = "<!-- example-start -->"
    end_marker = "<!-- example-end -->"
    try:
        start = text.index(start_marker) + len(start_marker)
        end = text.index(end_marker, start)
    except ValueError as exc:  # pragma: no cover - explicit failure path
        raise AssertionError("README example markers missing") from exc

    section = text[start:end]
    match = re.search(r"```python\n(.*?)\n```", section, re.DOTALL)
    if not match:
        raise AssertionError("No python code block found in README example section")

    monkeypatch.chdir(tmp_path)
    code = match.group(1)
    stdout = io.StringIO()
    exec_globals = {"__name__": "__main__"}

    with contextlib.redirect_stdout(stdout):
        exec(compile(code, str(README_PATH), "exec"), exec_globals)

    output = stdout.getvalue()
    assert "Symmetric key kid:" in output
    assert "Asymmetric key kid:" in output
    assert "Random token length:" in output
    assert "JWKS entries:" in output

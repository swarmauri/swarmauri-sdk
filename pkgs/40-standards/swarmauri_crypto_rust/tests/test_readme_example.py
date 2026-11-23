"""Tests that the README usage example remains executable."""

from __future__ import annotations

import contextlib
import io
import re
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parent.parent / "README.md"


@pytest.mark.example
def test_readme_usage_example_executes_successfully():
    """Execute the README usage example and assert that it reports success."""

    readme_contents = README_PATH.read_text(encoding="utf-8")
    match = re.search(r"```python\n(.*?)\n```", readme_contents, re.DOTALL)
    assert match, "Usage example code block not found in README.md"

    code = match.group(1)
    namespace: dict[str, object] = {
        "__builtins__": __builtins__,
        "__name__": "__main__",
    }
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exec(code, namespace)

    output = stdout.getvalue()
    assert "Match:     True" in output, output

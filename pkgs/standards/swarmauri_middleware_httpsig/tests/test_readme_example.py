"""Execute the README example to ensure it stays runnable."""

from __future__ import annotations

import pathlib
import re

import pytest


README_PATH = pathlib.Path(__file__).resolve().parents[1] / "README.md"
EXAMPLE_PATTERN = re.compile(r"## Example.*?```python\n(?P<code>.*?)\n```", re.S)


@pytest.mark.example
def test_readme_example_executes():
    """Run the README example and assert it remains valid."""

    content = README_PATH.read_text(encoding="utf-8")
    match = EXAMPLE_PATTERN.search(content)
    assert match, "Unable to locate example code block in README.md"

    code = match.group("code")
    exec_globals = {"__name__": "__main__"}
    exec(compile(code, str(README_PATH), "exec"), exec_globals)  # noqa: S102

"""Execute the README quickstart example to ensure it remains functional."""

from __future__ import annotations

import pathlib
import re

import pytest


@pytest.mark.example
def test_readme_quickstart_executes() -> None:
    """Load and execute the first Python example from the README."""

    readme_path = pathlib.Path(__file__).resolve().parents[2] / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    match = re.search(r"```python\n(.*?)\n```", readme_text, re.DOTALL)
    assert match, "README must contain a Python fenced code block"

    code_block = match.group(1)
    exec(compile(code_block, str(readme_path), "exec"), {})

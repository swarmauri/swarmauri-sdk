from __future__ import annotations

import re
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[2] / "README.md"
CODE_SNIPPET_PATTERN = re.compile(r"```python\n(?P<code>.*?)\n```", re.DOTALL)


@pytest.mark.example
def test_readme_example_executes() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    match = CODE_SNIPPET_PATTERN.search(readme)
    assert match, "README is missing a Python usage example"

    code = match.group("code")
    namespace: dict[str, object] = {
        "__name__": "__main__",
        "__builtins__": __builtins__,
    }
    exec(compile(code, str(README_PATH), "exec"), namespace)

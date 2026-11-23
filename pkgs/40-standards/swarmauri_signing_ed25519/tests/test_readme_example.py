from __future__ import annotations

import pathlib
import re
from typing import Any, Dict

import pytest


@pytest.mark.example
def test_readme_example_executes() -> None:
    readme = pathlib.Path(__file__).resolve().parent.parent / "README.md"
    text = readme.read_text(encoding="utf-8")
    match = re.search(
        r"<!-- example-start -->\s*```python\n(?P<code>.*?)```",
        text,
        flags=re.DOTALL,
    )
    assert match, "Example code block not found in README"

    namespace: Dict[str, Any] = {"__name__": "__main__"}
    code = match.group("code")
    exec(compile(code, str(readme), "exec"), namespace)
    assert namespace.get("verified") is True, (
        "README example should set `verified` to True"
    )

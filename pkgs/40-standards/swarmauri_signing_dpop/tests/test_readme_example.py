from __future__ import annotations

import re
import textwrap
from pathlib import Path

import pytest


@pytest.mark.example
def test_readme_example_executes() -> None:
    readme = Path(__file__).resolve().parents[1] / "README.md"
    content = readme.read_text(encoding="utf-8")
    match = re.search(r"```python\n(.*?)\n```", content, re.DOTALL)
    assert match is not None, "No python example found in README"

    code = textwrap.dedent(match.group(1))
    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(compile(code, str(readme), "exec"), namespace)

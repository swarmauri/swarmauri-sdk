from __future__ import annotations

import re
import textwrap
from pathlib import Path

import pytest


@pytest.mark.example
def test_readme_usage_example_executes() -> None:
    """Execute the README usage example to ensure it stays valid."""

    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    match = re.search(
        r"<!-- example-start -->\s*```python\n(?P<code>.*?)\n```",
        content,
        re.DOTALL,
    )
    assert match, (
        "Expected README usage example fenced by <!-- example-start --> markers."
    )

    example_src = textwrap.dedent(match.group("code"))
    compiled = compile(example_src, str(readme_path), "exec")
    exec_globals: dict[str, object] = {"__name__": "__main__"}
    exec(compiled, exec_globals)

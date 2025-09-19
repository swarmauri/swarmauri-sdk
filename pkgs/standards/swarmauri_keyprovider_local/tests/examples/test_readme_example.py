from __future__ import annotations

import asyncio
import re
import textwrap
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[2] / "README.md"


@pytest.mark.example
def test_readme_quickstart_example_runs() -> None:
    """Execute the Quickstart snippet from the README to keep it accurate."""

    readme = README_PATH.read_text(encoding="utf-8")
    match = re.search(r"## Quickstart.*?```python\n(.*?)```", readme, re.DOTALL)
    assert match, "Could not locate Quickstart python example in README"

    code = textwrap.dedent(match.group(1)).strip()
    namespace: dict[str, object] = {"__name__": "__readme__"}
    exec(code, namespace)  # noqa: S102 - executing trusted documentation example

    run_example = namespace.get("run_example")
    assert callable(run_example), "README example must define run_example()"

    result = asyncio.run(run_example())  # type: ignore[arg-type]
    assert isinstance(result, str)
    assert result

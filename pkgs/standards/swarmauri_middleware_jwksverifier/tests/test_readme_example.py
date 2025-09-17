from __future__ import annotations

from pathlib import Path
import textwrap

import pytest


@pytest.mark.example
def test_readme_example_executes() -> None:
    readme = Path(__file__).resolve().parents[1] / "README.md"
    contents = readme.read_text(encoding="utf-8")
    try:
        _, remainder = contents.split("```python", 1)
    except ValueError as exc:  # pragma: no cover - protects against README drift
        raise AssertionError("README is missing a Python example block") from exc
    code_block, _ = remainder.split("```", 1)
    code = textwrap.dedent(code_block).strip()

    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(code, namespace)  # noqa: S102 - intentional execution of documentation example

    assert namespace.get("claims")
    assert namespace["claims"].get("sub") == "user-123"

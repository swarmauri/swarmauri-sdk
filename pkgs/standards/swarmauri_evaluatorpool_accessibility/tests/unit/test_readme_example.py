"""Execute the README usage example to ensure it stays valid."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _readme_path() -> Path:
    return Path(__file__).resolve().parents[2] / "README.md"


def _extract_first_python_block(text: str) -> str:
    match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
    if not match:
        raise AssertionError("README is missing a python usage example")
    return match.group(1)


@pytest.mark.example
def test_readme_usage_example_executes() -> None:
    """Run the README example verbatim."""

    code = _extract_first_python_block(_readme_path().read_text(encoding="utf-8"))
    namespace: dict[str, object] = {}

    exec(compile(code, str(_readme_path()), "exec"), namespace)

    result = namespace.get("result")
    assert result is not None, "README example should assign the evaluation result"
    assert hasattr(result, "score"), "Result should expose a score attribute"

    pool = namespace.get("pool")
    if hasattr(pool, "shutdown"):
        pool.shutdown()

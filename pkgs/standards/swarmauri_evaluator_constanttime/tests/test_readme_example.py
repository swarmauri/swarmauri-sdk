"""Execute the README usage example to keep it working."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


def _extract_usage_example() -> str:
    text = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"```python\n(?P<code>.*?ConstantTimeEvaluator.*?)```", re.DOTALL
    )
    match = pattern.search(text)
    if not match:  # pragma: no cover - defensive guard to show clearer error
        raise AssertionError("Could not locate the README usage example.")
    return match.group("code").strip()


@pytest.mark.example
def test_readme_usage_example() -> None:
    code = _extract_usage_example()
    namespace = {"__name__": "__main__"}
    exec(compile(code, str(README_PATH), "exec"), namespace)  # noqa: S102

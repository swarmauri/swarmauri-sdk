"""README example tests for swarmauri_middleware_llamaguard."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


def _extract_basic_request_filtering_example() -> str:
    """Return the README example code block for basic request filtering."""

    content = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"```python\n# README Example: Basic request filtering\n(?P<code>.*?)```",
        re.DOTALL,
    )
    match = pattern.search(content)
    assert match, "README example code block not found."
    return match.group("code")


@pytest.mark.example
def test_readme_basic_request_filtering_example_executes() -> None:
    """Execute the README's basic request filtering example."""

    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(_extract_basic_request_filtering_example(), namespace)

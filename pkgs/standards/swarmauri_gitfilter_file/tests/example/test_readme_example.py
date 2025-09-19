from __future__ import annotations

import re
import textwrap
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parent.parent.parent / "README.md"


def _load_usage_example() -> str:
    content = README_PATH.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\s*(.*?)```", content, re.DOTALL)
    if not blocks:
        raise AssertionError("README.md does not contain a Python usage example")
    return textwrap.dedent(blocks[0]).strip()


@pytest.mark.example
def test_readme_usage_example_executes() -> None:
    code = _load_usage_example()
    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(code, namespace)

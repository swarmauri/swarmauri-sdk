from __future__ import annotations

import re
import textwrap
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[2] / "README.md"


def _extract_usage_snippet() -> str:
    contents = README_PATH.read_text(encoding="utf-8")
    try:
        usage_section = contents.split("## Usage", maxsplit=1)[1]
    except IndexError as exc:  # pragma: no cover - defensive clarity
        raise AssertionError("README missing usage section") from exc
    match = re.search(r"```python\n(.*?)```", usage_section, re.DOTALL)
    if not match:
        raise AssertionError("README usage example missing Python snippet")
    return textwrap.dedent(match.group(1))


@pytest.mark.example
def test_readme_usage_example() -> None:
    snippet = _extract_usage_snippet()
    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(snippet, namespace)

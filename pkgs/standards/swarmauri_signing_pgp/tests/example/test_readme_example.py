"""Execute the README usage example to ensure it stays accurate."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[2] / "README.md"


def _readme_usage_code() -> str:
    text = README_PATH.read_text(encoding="utf-8")
    match = re.findall(r"```python\n(.*?)```", text, flags=re.DOTALL)
    if not match:
        raise AssertionError("README example missing python code block.")
    return match[0]


@pytest.mark.example
def test_readme_usage_example(capsys: pytest.CaptureFixture[str]) -> None:
    capsys.readouterr()
    code = _readme_usage_code()
    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(code, namespace)
    captured = capsys.readouterr()
    assert "Verified: True" in captured.out

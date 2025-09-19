"""Ensure the README quickstart stays runnable."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parent.parent / "README.md"


@pytest.mark.example
def test_quickstart_example_runs(capsys: pytest.CaptureFixture[str]) -> None:
    """Execute the README quickstart example verbatim."""

    readme = README_PATH.read_text(encoding="utf-8")
    match = re.search(r"```python\n(?P<code>.*?)```", readme, re.DOTALL)
    assert match is not None, "Could not locate python example in README.md"

    code = match.group("code").strip()

    original_sys_path = list(sys.path)
    sys.path.insert(0, str(README_PATH.parent))
    try:
        exec(compile(code, str(README_PATH), "exec"), {"__name__": "__main__"})
    finally:
        sys.path[:] = original_sys_path

    captured = capsys.readouterr()
    assert "Recovered plaintext:" in captured.out

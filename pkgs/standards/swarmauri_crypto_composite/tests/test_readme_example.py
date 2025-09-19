from __future__ import annotations

import re
from pathlib import Path

import pytest


README = Path(__file__).resolve().parents[1] / "README.md"


def _extract_example_block() -> str:
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(r"```python\n(.*?)\n```", re.DOTALL)
    for match in pattern.finditer(text):
        block = match.group(1)
        if "CompositeCrypto" in block and "asyncio.run" in block:
            return block
    raise AssertionError("Unable to find README example block")


@pytest.mark.example
def test_readme_example_executes(capsys):
    code = _extract_example_block()
    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(compile(code, str(README), "exec"), namespace)
    captured = capsys.readouterr()
    assert "Selected provider: aes" in captured.out

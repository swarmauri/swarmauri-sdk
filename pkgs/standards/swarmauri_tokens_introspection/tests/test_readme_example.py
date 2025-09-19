"""README example regression tests."""

from __future__ import annotations

from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


def _load_python_example() -> str:
    in_block = False
    lines: list[str] = []
    for line in README_PATH.read_text().splitlines():
        if not in_block:
            if line.startswith("```python"):
                in_block = True
            continue
        if line.strip() == "```":
            break
        lines.append(line)
    return "\n".join(lines).strip()


@pytest.mark.example
def test_readme_usage_example_executes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = _load_python_example()
    assert code, "README python example not found"
    namespace = {"__name__": "__main__"}
    exec(compile(code, str(README_PATH), "exec"), namespace)
    out = capsys.readouterr().out
    assert "user-123" in out

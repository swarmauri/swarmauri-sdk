from __future__ import annotations

from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


def _extract_first_python_block(markdown: str) -> str:
    """Return the first fenced Python code block from the README."""

    in_block = False
    code_lines: list[str] = []

    for line in markdown.splitlines():
        stripped = line.strip()

        if not in_block:
            if stripped.startswith("```python"):
                in_block = True
            continue

        if stripped.startswith("```"):
            break

        code_lines.append(line)

    if not code_lines:
        raise AssertionError("No python example found in README.md")

    return "\n".join(code_lines)


@pytest.mark.example
def test_readme_example_executes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Execute the README example to ensure it remains runnable."""

    example_code = _extract_first_python_block(README_PATH.read_text())
    monkeypatch.syspath_prepend(str(README_PATH.parent))

    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(compile(example_code, str(README_PATH), "exec"), namespace)

    output = capsys.readouterr().out
    assert "Score: 0.50" in output
    assert "should be decorated with @abstractmethod" in output

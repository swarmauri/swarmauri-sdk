from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pytest


def _readme_python_example(readme_path: Path) -> str:
    lines = readme_path.read_text(encoding="utf-8").splitlines()
    example_lines: list[str] = []
    capturing = False

    for line in lines:
        stripped = line.strip()
        if not capturing and stripped.lower().startswith("```python"):
            capturing = True
            continue
        if capturing and stripped.startswith("```"):
            break
        if capturing:
            example_lines.append(line)

    if not example_lines:
        raise AssertionError("No python example found in README.md")

    return "\n".join(example_lines)


def _find_line(prefix: str, lines: Iterable[str]) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line
    raise AssertionError(f"Expected line starting with {prefix!r} in example output")


@pytest.mark.example
def test_readme_example_runs(capsys: pytest.CaptureFixture[str]) -> None:
    readme_path = Path(__file__).resolve().parents[2] / "README.md"
    code = _readme_python_example(readme_path)

    exec_globals = {"__name__": "__main__"}
    exec(compile(code, str(readme_path), "exec"), exec_globals)

    output = capsys.readouterr().out.splitlines()
    normalized = [line.strip() for line in output if line.strip()]

    assert "Cache-Control: max-age=60, public" in normalized

    etag_line = _find_line("ETag:", normalized)
    assert etag_line.split(":", 1)[1].strip(), "ETag header should not be empty"

    vary_line = _find_line("Vary:", normalized)
    assert vary_line == "Vary: Accept-Encoding"

    payload_line = _find_line("Payload:", normalized)
    assert payload_line.endswith("{'state': 'fresh'}")

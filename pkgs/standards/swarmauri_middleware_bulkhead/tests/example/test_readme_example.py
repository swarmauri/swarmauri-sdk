from __future__ import annotations

from pathlib import Path

import pytest


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
README_PATH = PACKAGE_ROOT / "README.md"


def _extract_quickstart_code(readme: str) -> str:
    in_quickstart = False
    in_code_block = False
    code_lines: list[str] = []

    for line in readme.splitlines():
        if line.strip() == "## Quickstart":
            in_quickstart = True
            continue

        if not in_quickstart:
            continue

        if line.startswith("```"):
            if line.startswith("```python") and not in_code_block:
                in_code_block = True
                continue
            if in_code_block:
                break

        if in_code_block:
            code_lines.append(line)

    code = "\n".join(code_lines).strip()
    if not code:
        raise AssertionError("Quickstart python code block not found in README")
    return code


@pytest.mark.example
def test_readme_quickstart_example(capsys: pytest.CaptureFixture[str]) -> None:
    readme_text = README_PATH.read_text(encoding="utf-8")
    code = _extract_quickstart_code(readme_text)

    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(compile(code, str(README_PATH), "exec"), namespace)

    captured = capsys.readouterr().out
    assert "Peak concurrent requests:" in captured
    assert "Responses:" in captured

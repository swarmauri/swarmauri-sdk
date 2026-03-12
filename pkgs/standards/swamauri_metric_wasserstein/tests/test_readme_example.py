from __future__ import annotations

from pathlib import Path

import pytest


def _extract_first_python_code_block(text: str) -> str:
    lines = text.splitlines()
    code_lines: list[str] = []
    in_block = False

    for line in lines:
        stripped = line.strip()
        if not in_block:
            if stripped == "```python":
                in_block = True
            continue

        if stripped == "```":
            break

        code_lines.append(line)

    return "\n".join(code_lines)


@pytest.mark.example
def test_readme_example_executes() -> None:
    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    code_block = _extract_first_python_code_block(
        readme_path.read_text(encoding="utf-8")
    )

    assert code_block, "README.md must contain a Python example code block"

    namespace: dict[str, object] = {}
    exec(code_block, namespace)

    assert namespace["distance"] == 0.0
    assert namespace["similarity"] == 1.0

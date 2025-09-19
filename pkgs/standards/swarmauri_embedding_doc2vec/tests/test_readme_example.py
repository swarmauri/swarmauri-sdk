"""Execute the README example to ensure it stays in sync with the package."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

import pytest


_README_PATH: Final[Path] = Path(__file__).resolve().parents[1] / "README.md"


def _extract_readme_example() -> str:
    content = _README_PATH.read_text(encoding="utf-8").splitlines()
    in_block = False
    code_lines: list[str] = []

    for line in content:
        stripped = line.strip()
        if not in_block and stripped.startswith("```python"):
            in_block = True
            continue
        if in_block and stripped.startswith("```"):
            break
        if in_block:
            code_lines.append(line)

    return "\n".join(code_lines)


@pytest.mark.example
def test_readme_example(tmp_path: Path) -> None:
    code = _extract_readme_example()
    assert code.strip(), "Expected a Python example code block in the README."

    original_cwd = Path.cwd()
    namespace: dict[str, object] = {}

    try:
        os.chdir(tmp_path)
        exec(code, namespace)
    finally:
        os.chdir(original_cwd)

    model_path = tmp_path / "doc2vec.model"
    assert model_path.exists(), "The README example should persist the trained model."

    vectors = namespace.get("vectors")
    new_vector = namespace.get("new_vector")

    assert isinstance(vectors, list) and len(vectors) == 3
    assert all(hasattr(vec, "value") for vec in vectors)
    assert new_vector is not None and hasattr(new_vector, "value")

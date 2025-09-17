"""Execute the README examples to ensure they stay accurate."""

from __future__ import annotations

from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[1] / "README.md"


def _python_code_blocks(readme: str) -> list[str]:
    blocks: list[str] = []
    in_block = False
    current: list[str] = []

    for line in readme.splitlines():
        if line.startswith("```python"):
            in_block = True
            current = []
            continue
        if in_block and line.startswith("```"):
            blocks.append("\n".join(current))
            in_block = False
            current = []
            continue
        if in_block:
            current.append(line)

    return blocks


@pytest.mark.example
def test_readme_examples(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    readme_text = README_PATH.read_text(encoding="utf-8")
    examples = _python_code_blocks(readme_text)

    assert len(examples) >= 2, (
        "Expected at least two python code examples in the README"
    )

    # Execute the inline template example.
    inline_namespace: dict[str, object] = {}
    exec(examples[0], inline_namespace)
    assert inline_namespace["result"] == "Hello, World!"

    # Run the filesystem-backed example inside an isolated working directory.
    fs_namespace: dict[str, object] = {}
    example_dir = tmp_path / "readme"
    example_dir.mkdir()
    monkeypatch.chdir(example_dir)
    exec(examples[1], fs_namespace)

    prompt = fs_namespace["prompt"]
    assert callable(prompt)
    assert prompt({"animal": "fox"}) == "Hello, foxes!"

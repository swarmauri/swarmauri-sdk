from __future__ import annotations

import pathlib
import textwrap

import pytest


_README = pathlib.Path(__file__).resolve().parent.parent / "README.md"


def _extract_usage_snippet(text: str) -> str:
    marker = "## Usage"
    start = text.index(marker)
    block_start = text.index("```python", start)
    block_end = text.index("```", block_start + len("```python"))
    snippet = text[block_start + len("```python") : block_end]
    return textwrap.dedent(snippet).strip()


@pytest.mark.example
def test_readme_usage_example(capsys: pytest.CaptureFixture[str]) -> None:
    snippet = _extract_usage_snippet(_README.read_text(encoding="utf-8"))
    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(compile(snippet, str(_README), "exec"), namespace)
    captured = capsys.readouterr()
    assert captured.out.strip().endswith('{"msg":"hi"}')

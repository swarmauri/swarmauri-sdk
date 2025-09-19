"""Execute README examples to ensure documentation stays accurate."""

from __future__ import annotations

import io
import re
from contextlib import redirect_stdout
from pathlib import Path

import pytest

README_PATH = Path(__file__).resolve().parents[1] / "README.md"
CODE_BLOCK_PATTERN = re.compile(r"```python\n(.*?)```", re.DOTALL)


@pytest.mark.example
def test_sort_file_records_snippet_executes() -> None:
    """Run the README dependency-ordering example and verify the output."""
    readme_text = README_PATH.read_text(encoding="utf-8")
    blocks = CODE_BLOCK_PATTERN.findall(readme_text)
    target_block = next(
        (block for block in blocks if "sort_file_records" in block), None
    )
    assert target_block is not None, "README sort_file_records example not found"

    stdout = io.StringIO()
    namespace: dict[str, object] = {}
    with redirect_stdout(stdout):
        exec(compile(target_block, str(README_PATH), "exec"), namespace)

    output_lines = stdout.getvalue().strip().splitlines()
    assert output_lines == [
        "['README.md', 'components/db.py', 'components/service.py']",
        "3",
    ]

from __future__ import annotations

import re
from pathlib import Path

import pytest


@pytest.mark.example
def test_readme_python_example_runs(capsys):
    """Ensure the Python example in the README executes without errors."""

    readme_path = Path(__file__).resolve().parents[2] / "README.md"
    readme_content = readme_path.read_text(encoding="utf-8")

    code_block = re.search(r"```python\n(.*?)\n```", readme_content, re.DOTALL)
    assert code_block, "Python example not found in README.md"

    code = code_block.group(1)

    exec_globals: dict[str, object] = {"__name__": "__main__"}
    exec(compile(code, str(readme_path), "exec"), exec_globals)

    captured = capsys.readouterr()
    assert "Allowed origin header: https://frontend.example" in captured.out
    assert "Response JSON: {'status': 'ok'}" in captured.out

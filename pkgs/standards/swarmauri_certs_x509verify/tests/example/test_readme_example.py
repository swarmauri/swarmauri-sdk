"""Execute the README quick start example to guard against drift."""

from __future__ import annotations

import io
import re
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.mark.example
def test_readme_quick_start_example() -> None:
    """Run the documented example and validate the observable results."""

    readme_path = Path(__file__).resolve().parents[2] / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    code_blocks = re.findall(r"```python\n(.*?)```", readme_text, flags=re.DOTALL)
    sentinel = "# README example: verify and parse a development certificate"

    snippet = next((block for block in code_blocks if sentinel in block), None)
    assert snippet is not None, "README quick start example not found"

    namespace: Dict[str, Any] = {"__builtins__": __builtins__}
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        exec(compile(snippet, str(readme_path), "exec"), namespace)

    output = buffer.getvalue()
    assert "CN=example.test" in output
    assert "True" in output.splitlines()[-1]

    example_result = namespace.get("example_result")
    assert isinstance(example_result, dict), (
        "README example did not expose example_result"
    )

    parsed = example_result["parsed"]
    verification = example_result["verification"]

    assert parsed["subject"] == "CN=example.test"
    assert verification["valid"] is True
    assert verification["reason"] is None
    assert verification["revocation_checked"] is False

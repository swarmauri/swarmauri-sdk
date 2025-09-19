"""Execute the README example to guard against drift."""

from __future__ import annotations

import io
import re
from contextlib import redirect_stdout
from pathlib import Path

import pytest

README_PATH = Path(__file__).resolve().parents[2] / "README.md"


@pytest.mark.example
@pytest.mark.timeout(30)
def test_readme_usage_example() -> None:
    """Run the README example and assert the expected output."""

    readme = README_PATH.read_text(encoding="utf-8")

    code_block: str | None = None
    pattern = re.compile(r"```python\n(.*?)\n```", re.DOTALL)
    for match in pattern.finditer(readme):
        candidate = match.group(1)
        if "RemoteOIDCTokenService" in candidate:
            code_block = candidate
            break

    assert code_block, "Unable to locate README example"

    stdout = io.StringIO()
    namespace: dict[str, object] = {"__name__": "__main__"}
    with redirect_stdout(stdout):
        exec(code_block, namespace)  # noqa: S102 - executing trusted documentation

    output = stdout.getvalue()
    assert "Verified subject: user-123" in output

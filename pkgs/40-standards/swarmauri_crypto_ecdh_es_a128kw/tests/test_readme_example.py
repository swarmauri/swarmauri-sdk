import re
from pathlib import Path

import pytest


README = Path(__file__).resolve().parents[1] / "README.md"


@pytest.mark.example
def test_quickstart_example_executes() -> None:
    """Execute the README quickstart example to ensure it stays valid."""
    contents = README.read_text(encoding="utf-8")
    match = re.search(r"```python\n(.*?)\n```", contents, re.DOTALL)
    if match is None:
        pytest.fail("Could not locate python example in README.md")

    code = match.group(1)
    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(compile(code, str(README), "exec"), namespace)

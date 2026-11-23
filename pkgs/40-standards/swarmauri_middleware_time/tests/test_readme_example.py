from pathlib import Path
import re

import pytest


@pytest.mark.example
def test_readme_example_runs():
    """Execute the README example to ensure it stays up to date."""

    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    code_blocks = re.findall(r"```python\n(.*?)\n```", readme_text, re.DOTALL)
    example_block = next(
        (block for block in code_blocks if "TimerMiddleware" in block),
        None,
    )

    assert example_block is not None, (
        "Unable to find README example for TimerMiddleware"
    )

    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(example_block, namespace)

    response = namespace.get("response")
    assert response is not None, "README example did not define a response"
    assert "X-Request-Duration" in response.headers
    assert float(response.headers["X-Request-Duration"]) >= 0.0
    assert "X-Request-Start-Time" in response.headers

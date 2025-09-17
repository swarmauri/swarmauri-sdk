"""Execute the README usage example to keep documentation accurate."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

import pytest

pytest.importorskip("fastapi")

README_PATH: Final[Path] = Path(__file__).resolve().parents[2] / "README.md"


def _extract_usage_snippet() -> str:
    """Return the README's primary usage example."""
    content = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(r"```python\n(?P<code>.*?)```", re.DOTALL)

    for match in pattern.finditer(content):
        code = match.group("code").strip()
        if "ExceptionHandlingMiddleware" in code and "TestClient" in code:
            return code

    raise AssertionError("README usage example not found")


@pytest.mark.example
@pytest.mark.test
def test_readme_usage_example() -> None:
    """Execute the README usage snippet and validate the response payload."""

    namespace: dict[str, object] = {}
    exec(_extract_usage_snippet(), namespace)

    response = namespace.get("response")
    assert response is not None, "README example must assign a `response` variable."

    status_code = getattr(response, "status_code", None)
    assert status_code == 500, (
        "README example should demonstrate the 500 error response."
    )

    json_method = getattr(response, "json", None)
    assert callable(json_method), (
        "README example response must provide a .json() accessor."
    )

    payload = json_method()
    assert isinstance(payload, dict)
    assert payload.get("error", {}).get("type") == "Unhandled Exception"
    assert payload.get("error", {}).get("message") == "Boom!"
    assert "timestamp" in payload.get("error", {})

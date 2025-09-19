from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

from swarmauri_middleware_securityheaders import SecurityHeadersMiddleware


CODE_BLOCK_PATTERN = re.compile(r"```python\n(?P<code>.*?)\n```", re.DOTALL)


@pytest.mark.example
def test_readme_usage_example_executes() -> None:
    """Execute the README usage example and confirm headers are applied."""

    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    match = CODE_BLOCK_PATTERN.search(readme_text)
    assert match is not None, "Could not locate python example in README.md"

    namespace: dict[str, Any] = {}
    exec(match.group("code"), namespace)

    app = namespace.get("app")
    assert isinstance(app, FastAPI), "README example did not define a FastAPI app"

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    control_response = Response()

    def _dummy_app(*args: Any, **kwargs: Any) -> Response:
        return control_response

    SecurityHeadersMiddleware(_dummy_app)._add_security_headers(control_response)

    expected_headers = {
        header: value
        for header, value in control_response.headers.items()
        if header
        in {
            "Content-Security-Policy",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Referrer-Policy",
            "Permissions-Policy",
        }
    }

    for header, expected_value in expected_headers.items():
        assert response.headers.get(header) == expected_value

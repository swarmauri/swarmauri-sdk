import logging
import re
import textwrap
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _load_usage_example() -> str:
    readme_path = Path(__file__).resolve().parents[2] / "README.md"
    content = readme_path.read_text(encoding="utf-8")
    match = re.search(r"```python\n(.*?)```", content, re.DOTALL)
    if not match:
        raise AssertionError("Usage example code block not found in README.md")
    return textwrap.dedent(match.group(1))


@pytest.mark.example
def test_readme_usage_example(caplog: pytest.LogCaptureFixture) -> None:
    source = _load_usage_example()
    namespace: dict[str, object] = {}
    exec(source, namespace)  # noqa: S102 - executing README example

    app = namespace.get("app")
    if app is None:
        raise AssertionError("README example did not define an 'app' instance")

    with caplog.at_level(logging.INFO):
        client = TestClient(app)
        response = client.get("/")

    assert response.json() == {"message": "hello"}

    middleware_logs = [
        record.getMessage()
        for record in caplog.records
        if record.name == "swarmauri_middleware_stdio.StdioMiddleware"
    ]
    assert any("STDIO Request: GET /" in message for message in middleware_logs)
    assert any("STDIO Response: 200" in message for message in middleware_logs)

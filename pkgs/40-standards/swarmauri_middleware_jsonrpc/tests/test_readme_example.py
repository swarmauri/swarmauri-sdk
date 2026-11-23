"""Tests that the README usage example continues to function."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient


@pytest.mark.example
def test_readme_usage_example() -> None:
    """Execute the README example and verify middleware behaviour."""

    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")
    code_blocks = re.findall(r"```python\n(.*?)```", readme_text, re.DOTALL)
    assert code_blocks, "Expected at least one Python example in README.md"

    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(compile(code_blocks[0], str(readme_path), "exec"), namespace)

    app = namespace.get("app")
    assert isinstance(app, Starlette), (
        "README example must define a Starlette app"
    )

    async def echo(request: Request) -> JSONResponse:
        return JSONResponse({"payload": await request.json()})

    app.add_route("/echo", echo, methods=["POST"])
    client = TestClient(app)

    missing_jsonrpc = client.post("/echo", json={"method": "ping"})
    assert missing_jsonrpc.status_code == 400
    assert "jsonrpc" in missing_jsonrpc.text

    invalid_json = client.post(
        "/echo",
        content="not json",
        headers={"content-type": "application/json"},
    )
    assert invalid_json.status_code == 400
    assert "Invalid JSON" in invalid_json.text

    valid_jsonrpc = client.post(
        "/echo",
        json={"jsonrpc": "2.0", "method": "ping"},
    )
    assert valid_jsonrpc.status_code == 200
    assert valid_jsonrpc.json() == {
        "payload": {"jsonrpc": "2.0", "method": "ping"}
    }

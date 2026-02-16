from __future__ import annotations

from tigrbl.headers import Headers
from tigrbl.responses import Response


def test_response_headers_support_dot_notation_access_and_assignment() -> None:
    headers = Headers({"Content-Type": "application/json"})

    assert headers.content_type == "application/json"

    headers.x_trace_id = "trace-123"
    assert headers["x-trace-id"] == "trace-123"


def test_response_exposes_dot_notation_attributes_without_getattr_helpers() -> None:
    response = Response.text("ok", headers={"X-Request-Id": "req-1"})

    assert response.status_code == 200
    assert response.body_text == "ok"
    assert response.headers_map.x_request_id == "req-1"

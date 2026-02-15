from __future__ import annotations

from tigrbl.transport.request import Headers, Request


def test_request_headers_support_dot_notation_access_and_assignment() -> None:
    headers = Headers({"X-Trace-Id": "abc123"})

    assert headers.x_trace_id == "abc123"

    headers.authorization = "Bearer token"
    assert headers["authorization"] == "Bearer token"


def test_request_exposes_dot_notation_attributes_without_getattr_helpers() -> None:
    request = Request(
        method="GET",
        path="/health",
        headers={"Cookie": "session=abc123"},
        query={"page": ["1"]},
        path_params={},
        body=b"",
    )

    assert request.path == "/health"
    assert request.url.path == "/health"
    assert request.query_params["page"] == "1"
    assert request.cookies["session"] == "abc123"

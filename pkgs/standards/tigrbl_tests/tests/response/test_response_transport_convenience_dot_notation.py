from __future__ import annotations

from tigrbl.responses import Response


def test_response_supports_instance_json_method_for_body_payload() -> None:
    response = Response(
        status_code=200,
        headers=[("content-type", "application/json; charset=utf-8")],
        body=b'{"ok":true,"count":1}',
    )

    assert response.json() == {"ok": True, "count": 1}


def test_response_headers_and_cookies_support_dot_notation() -> None:
    response = Response(
        status_code=200,
        headers=[
            ("x-request-id", "req-123"),
            ("set-cookie", "sid=session-token; Path=/"),
        ],
        body=b"",
    )

    assert response.headers_map.x_request_id == "req-123"
    assert response.cookies.sid == "session-token"

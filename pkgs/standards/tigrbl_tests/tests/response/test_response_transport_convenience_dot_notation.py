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
    assert response.headers.get("x-request-id") == "req-123"
    assert "sid" in response.headers.get("set-cookie", "")
    assert response.cookies.sid == "session-token"


def test_response_set_cookie_supports_many_cookies_and_terse_reads() -> None:
    response = Response(status_code=200, headers=[], body=b"")

    response.set_cookie("sid", "session-token", path="/")
    response.set_cookie("tenant", "acme", path="/")
    response.set_cookie("theme", "dark", path="/")

    set_cookie_header = response.headers.get("set-cookie", "")
    assert "sid=session-token" in set_cookie_header
    assert "tenant=acme" in set_cookie_header
    assert "theme=dark" in set_cookie_header
    assert "session-token" in set_cookie_header.get("sid", "")
    assert "acme" in set_cookie_header.get("tenant", "")
    assert "dark" in set_cookie_header.get("theme", "")
    assert set_cookie_header.get("missing") is None

    assert response.cookies.sid == "session-token"
    assert response.cookies.tenant == "acme"
    assert response.cookies.theme == "dark"

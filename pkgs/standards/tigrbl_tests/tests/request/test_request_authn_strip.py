from __future__ import annotations

from tigrbl.requests import Request


def _make_request(*, headers: dict[str, str]) -> Request:
    return Request(
        method="GET",
        path="/authn",
        headers=headers,
        query={},
        path_params={},
        body=b"",
    )


def test_request_admin_key_is_stripped() -> None:
    request = _make_request(headers={"X-Admin-Key": "  admin-secret  "})

    assert request.admin_key == "admin-secret"


def test_request_bearer_session_token_is_stripped() -> None:
    request = _make_request(headers={"Authorization": "Bearer   public-token  "})

    assert request.bearer_token == "public-token"
    assert request.session_token == "public-token"


def test_request_cookie_session_token_is_stripped() -> None:
    request = _make_request(headers={"Cookie": "sid=  session-cookie-token  "})

    assert request.session_token == "session-cookie-token"

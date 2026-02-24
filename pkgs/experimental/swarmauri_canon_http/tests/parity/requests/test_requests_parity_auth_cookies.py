import requests
import pytest

from swarmauri_canon_http import HttpClient
from tests.parity.requests.helpers import build_prepared_request, build_session


def test_requests_supports_auth_on_prepared_request():
    prepared = build_prepared_request(
        "GET", "https://example.com", auth=("username", "password")
    )

    assert prepared.headers["Authorization"].startswith("Basic ")


def test_requests_session_supports_cookie_jar():
    session = build_session()
    session.cookies.set("session", "abc")
    prepared = session.prepare_request(requests.Request("GET", "https://example.com"))
    session.close()

    assert "session=abc" in prepared.headers.get("Cookie", "")


def test_canon_client_rejects_auth_and_cookies_constructor_keywords():
    with pytest.raises(TypeError):
        HttpClient(base_url="https://example.com", auth=("username", "password"))

    with pytest.raises(TypeError):
        HttpClient(base_url="https://example.com", cookies={"session": "abc"})

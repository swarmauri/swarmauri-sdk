import httpx
import pytest

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import build_httpx_request


def test_httpx_supports_auth_argument_on_client_and_request():
    request = build_httpx_request(
        "GET", "https://example.com", auth=("username", "password")
    )
    client = httpx.Client(auth=("username", "password"))
    client.close()

    assert request.headers["authorization"].startswith("Basic ")


def test_canon_client_rejects_auth_constructor_keyword():
    with pytest.raises(TypeError):
        HttpClient(base_url="https://example.com", auth=("username", "password"))


def test_httpx_supports_cookie_jar_and_per_request_cookies():
    client = httpx.Client(cookies={"session": "abc"})
    request = client.build_request("GET", "https://example.com", cookies={"scope": "1"})
    client.close()

    assert "session=abc" in request.headers["cookie"]
    assert "scope=1" in request.headers["cookie"]


def test_canon_client_rejects_cookies_constructor_keyword():
    with pytest.raises(TypeError):
        HttpClient(base_url="https://example.com", cookies={"session": "abc"})

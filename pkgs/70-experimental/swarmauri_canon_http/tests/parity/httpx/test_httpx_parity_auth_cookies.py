import httpx
import pytest

from swarmauri_canon_http import HttpClient


def test_httpx_supports_auth_argument_on_client_and_request():
    request = httpx.Request("GET", "https://example.com")
    request = next(httpx.BasicAuth("username", "password").auth_flow(request))
    client = httpx.Client(auth=("username", "password"))
    client.close()

    assert request.headers["authorization"].startswith("Basic ")


def test_canon_client_rejects_auth_constructor_keyword():
    with pytest.raises(TypeError):
        HttpClient(
            base_url="https://example.com", auth=("username", "password")
        )


def test_httpx_supports_cookie_jar_and_per_request_cookies():
    client = httpx.Client(cookies={"session": "abc"})
    request = client.build_request(
        "GET", "https://example.com", cookies={"scope": "1"}
    )
    client.close()

    assert "session=abc" in request.headers["cookie"]
    assert "scope=1" in request.headers["cookie"]


def test_canon_client_rejects_cookies_constructor_keyword():
    with pytest.raises(TypeError):
        HttpClient(base_url="https://example.com", cookies={"session": "abc"})

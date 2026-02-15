from __future__ import annotations

import httpx
import pytest

from swarmauri_canon_http import HttpClient
from tests.parity.httpx.helpers import build_httpx_request


def _build_sample_transport(**kwargs):
    return httpx.ASGITransport(app=lambda scope: None, **kwargs)


def test_httpx_asgi_transport_exists_and_is_constructible():
    transport = _build_sample_transport()
    request = build_httpx_request("GET", "http://example.com")

    assert isinstance(transport, httpx.ASGITransport)
    assert request.method == "GET"


def test_httpx_asgi_transport_supports_raise_app_exceptions_flag():
    transport = _build_sample_transport(raise_app_exceptions=False)

    assert isinstance(transport, httpx.ASGITransport)
    assert transport.raise_app_exceptions is False


def test_httpx_asgi_transport_supports_root_path_configuration():
    transport = _build_sample_transport(root_path="/service")

    assert isinstance(transport, httpx.ASGITransport)
    assert transport.root_path == "/service"


def test_httpx_asgi_transport_supports_client_configuration():
    transport = _build_sample_transport(client=("127.0.0.1", 6543))

    assert isinstance(transport, httpx.ASGITransport)
    assert transport.client == ("127.0.0.1", 6543)


@pytest.mark.asyncio
async def test_httpx_asgi_transport_is_usable_with_async_client():
    async def app(scope, receive, send):
        assert scope["type"] == "http"
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"text/plain")],
            }
        )
        await send({"type": "http.response.body", "body": b"ok"})

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.text == "ok"


def test_canon_client_has_no_asgi_transport_constructor_parity():
    with pytest.raises(TypeError):
        HttpClient(
            base_url="http://example.com",
            transport=httpx.ASGITransport(app=lambda s: None),
        )


@pytest.mark.parametrize(
    "transport_kwargs",
    [
        {"raise_app_exceptions": False},
        {"root_path": "/service"},
        {"client": ("127.0.0.1", 6543)},
    ],
)
def test_canon_client_has_no_asgi_transport_option_parity(transport_kwargs):
    with pytest.raises(TypeError):
        HttpClient(base_url="http://example.com", **transport_kwargs)

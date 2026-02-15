from __future__ import annotations

import json

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


@pytest.mark.asyncio
async def test_httpx_asgi_transport_populates_asgi_scope_with_request_details():
    captured_scope: dict[str, object] = {}

    async def app(scope, receive, send):
        captured_scope.update(scope)

        await send(
            {
                "type": "http.response.start",
                "status": 204,
                "headers": [],
            }
        )
        await send({"type": "http.response.body", "body": b""})

    transport = httpx.ASGITransport(
        app=app,
        root_path="/service",
        client=("192.0.2.10", 9090),
    )

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        await client.get("/status?ready=yes")

    assert captured_scope["type"] == "http"
    assert captured_scope["method"] == "GET"
    assert captured_scope["path"] == "/status"
    assert captured_scope["query_string"] == b"ready=yes"
    assert captured_scope["root_path"] == "/service"
    assert captured_scope["client"] == ("192.0.2.10", 9090)


@pytest.mark.asyncio
async def test_httpx_asgi_transport_forwards_request_body_to_receive_channel():
    received_messages: list[dict[str, object]] = []

    async def app(scope, receive, send):
        while True:
            message = await receive()
            received_messages.append(message)
            if not message.get("more_body", False):
                break

        body = b"".join(message.get("body", b"") for message in received_messages)
        payload = json.dumps(
            {
                "method": scope["method"],
                "body": body.decode("utf-8"),
                "message_count": len(received_messages),
            }
        ).encode("utf-8")

        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send({"type": "http.response.body", "body": payload})

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post("/submit", content=b"hello-asgi")

    assert response.status_code == 200
    assert response.json()["method"] == "POST"
    assert response.json()["body"] == "hello-asgi"
    assert response.json()["message_count"] >= 1


@pytest.mark.asyncio
async def test_httpx_asgi_transport_propagates_application_errors_when_enabled():
    async def app(scope, receive, send):
        raise RuntimeError("application crashed")

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=True)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        with pytest.raises(RuntimeError, match="application crashed"):
            await client.get("/")


@pytest.mark.asyncio
async def test_httpx_asgi_transport_converts_application_errors_to_500_response_when_disabled():
    async def app(scope, receive, send):
        raise RuntimeError("application crashed")

    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 500
    assert response.text == ""


@pytest.mark.asyncio
async def test_httpx_asgi_transport_preserves_repeated_response_headers():
    async def app(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"set-cookie", b"a=1"),
                    (b"set-cookie", b"b=2"),
                    (b"x-custom", b"value"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": b"ok"})

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.headers.get_list("set-cookie") == ["a=1", "b=2"]
    assert response.headers["x-custom"] == "value"


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

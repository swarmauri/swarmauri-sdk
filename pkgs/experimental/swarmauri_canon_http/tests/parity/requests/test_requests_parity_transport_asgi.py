from __future__ import annotations

import importlib

import httpx
import pytest

from ..transport_dependency_helpers import assert_transport_dependency_parity


def _load_swarmauri_transport_asgi():
    try:
        return importlib.import_module("swarmauri_transport_asgi")
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(
            f"swarmauri_transport_asgi is unavailable in this environment: {exc}",
            allow_module_level=False,
        )


def _build_httpx_sample_transport(**kwargs):
    return httpx.ASGITransport(app=lambda scope: None, **kwargs)


async def _noop_asgi_app(scope, receive, send):
    return None


def _build_swarmauri_sample_transport(app=None, **kwargs):
    swarmauri_transport_asgi = _load_swarmauri_transport_asgi()

    if app is None:
        app = _noop_asgi_app
    return swarmauri_transport_asgi.ASGITransport(app=app, **kwargs)


def test_requests_transport_parity_asgi():
    assert_transport_dependency_parity(
        transport_package="swarmauri_transport_asgi",
        parity_distribution_name="requests",
    )


def test_swarmauri_asgi_transport_is_constructible_like_httpx_with_app():
    swarmauri_transport_asgi = _load_swarmauri_transport_asgi()

    httpx_transport = _build_httpx_sample_transport()
    swarmauri_transport = _build_swarmauri_sample_transport()

    assert isinstance(httpx_transport, httpx.ASGITransport)
    assert isinstance(swarmauri_transport, swarmauri_transport_asgi.ASGITransport)


@pytest.mark.parametrize(
    "transport_kwargs",
    [
        {"raise_app_exceptions": False},
        {"root_path": "/service"},
        {"client": ("127.0.0.1", 6543)},
    ],
)
def test_swarmauri_asgi_transport_has_no_httpx_specific_constructor_options(
    transport_kwargs,
):
    _load_swarmauri_transport_asgi()

    _build_httpx_sample_transport(**transport_kwargs)

    with pytest.raises(TypeError):
        _build_swarmauri_sample_transport(app=_noop_asgi_app, **transport_kwargs)


@pytest.mark.asyncio
async def test_swarmauri_asgi_transport_is_not_usable_as_httpx_async_client_transport():
    _load_swarmauri_transport_asgi()

    async def app(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"text/plain")],
            }
        )
        await send({"type": "http.response.body", "body": b"ok"})

    httpx_transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=httpx_transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.text == "ok"

    swarmauri_transport = _build_swarmauri_sample_transport(app=app)
    with pytest.raises(AttributeError):
        async with httpx.AsyncClient(
            transport=swarmauri_transport,
            base_url="http://testserver",
        ) as client:
            await client.get("/")

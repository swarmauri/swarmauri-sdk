import httpx
import pytest
from swarmauri_core.transports import HttpStatusError

from swarmauri_transport_httpx import HttpxClient


def test_httpx_client_is_concrete():
    assert not HttpxClient.__abstractmethods__


def test_resolve_url():
    client = HttpxClient(base_url="https://example.test/v1")
    assert client.resolve_url("models") == "https://example.test/v1/models"


def test_client_reuses_injected_client_and_forwards_json():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    injected = httpx.Client(transport=httpx.MockTransport(handler))
    client = HttpxClient(
        base_url="https://example.test/v1",
        default_headers={"X-Default": "yes"},
        client=injected,
    )

    first = client.request("POST", "models", json={"name": "test"})
    second = client.request("GET", "models", params={"page": "2"})

    assert first.json() == {"ok": True}
    assert second.status_code == 200
    assert len(requests) == 2
    assert requests[0].headers["X-Default"] == "yes"
    client.close()
    assert not injected.is_closed
    injected.close()


def test_response_translates_status_errors():
    injected = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(429, request=request)
        )
    )
    client = HttpxClient(client=injected)
    response = client.request("GET", "https://example.test")

    with pytest.raises(HttpStatusError) as error:
        response.raise_for_status()

    assert error.value.status_code == 429
    injected.close()


def test_owned_client_is_lazy_reused_and_closed():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    client = HttpxClient(
        client_options={"transport": httpx.MockTransport(handler)}
    )
    assert client._sync_client is None
    client.request("GET", "https://example.test/one")
    owned = client._sync_client
    client.request("GET", "https://example.test/two")

    assert len(requests) == 2
    assert client._sync_client is owned
    client.close()
    assert owned.is_closed


@pytest.mark.asyncio
async def test_async_client_is_reused_and_caller_owned():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True})

    injected = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = HttpxClient(async_client=injected)
    assert (
        await client.arequest("GET", "https://example.test")
    ).status_code == 200
    assert (
        await client.arequest("GET", "https://example.test/2")
    ).status_code == 200
    assert len(requests) == 2
    await client.aclose()
    assert not injected.is_closed
    await injected.aclose()

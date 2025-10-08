import json

import httpx
import pytest

from tigrbl_spiffe.adapters import Txn
from tigrbl_spiffe.workload_client import WorkloadClientError, fetch_remote_svid


@pytest.mark.asyncio
async def test_fetch_remote_svid_jwt_via_http():
    token = "header.payload.signature"

    def responder(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/workload/jwtsvid"
        payload = json.loads(request.content.decode("utf-8"))
        assert payload["aud"] == ["demo"]
        return httpx.Response(
            200,
            json={
                "spiffe_id": "spiffe://example/client",
                "jwt": token,
                "aud": ["demo"],
                "nbf": 10,
                "exp": 20,
            },
        )

    transport = httpx.MockTransport(responder)
    client = httpx.AsyncClient(transport=transport, base_url="http://agent.test")
    txn = Txn(kind="http", http=client)
    try:
        result = await fetch_remote_svid(txn, kind="jwt", audiences=("demo",))
    finally:
        await client.aclose()

    assert result == {
        "spiffe_id": "spiffe://example/client",
        "kind": "jwt",
        "not_before": 10,
        "not_after": 20,
        "audiences": ("demo",),
        "material": token.encode("utf-8"),
        "bundle_id": None,
    }


@pytest.mark.asyncio
async def test_fetch_remote_svid_missing_token_raises():
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"spiffe_id": "spiffe://example/missing"})

    transport = httpx.MockTransport(responder)
    client = httpx.AsyncClient(transport=transport, base_url="http://agent.test")
    txn = Txn(kind="http", http=client)
    try:
        with pytest.raises(WorkloadClientError):
            await fetch_remote_svid(txn, kind="jwt", audiences=())
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_fetch_remote_svid_missing_spiffe_id_raises():
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"jwt": "token-value"})

    transport = httpx.MockTransport(responder)
    client = httpx.AsyncClient(transport=transport, base_url="http://agent.test")
    txn = Txn(kind="http", http=client)
    try:
        with pytest.raises(WorkloadClientError):
            await fetch_remote_svid(txn, kind="jwt", audiences=())
    finally:
        await client.aclose()

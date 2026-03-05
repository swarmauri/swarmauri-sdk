from __future__ import annotations

import httpx
import pytest

from tests.i9n.transport_parity_app import app
from tests.i9n.uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


async def _collect_transport_response(
    *,
    base_url: str,
    transport: str,
    use_http2: bool,
) -> dict[str, object]:
    headers = {"x-transport": transport}

    async with httpx.AsyncClient(http2=use_http2) as client:
        rest_response = await client.get(
            f"{base_url}/transport-widget", headers=headers
        )

        rpc_payload = {
            "jsonrpc": "2.0",
            "method": "TransportWidget.create",
            "params": {"name": f"{transport}-widget"},
            "id": transport,
        }
        rpc_response = await client.post(
            f"{base_url}/rpc/", json=rpc_payload, headers=headers
        )

    return {
        "transport": transport,
        "rest": {
            "status": rest_response.status_code,
            "body": rest_response.json(),
            "http_version": rest_response.http_version,
        },
        "jsonrpc": {
            "status": rpc_response.status_code,
            "body": rpc_response.json(),
            "http_version": rpc_response.http_version,
        },
    }


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_tigrblapp_transport_parity_h1_h2_h3() -> None:
    """Validate request/response parity for h1/h2/h3-style clients via uvicorn."""
    base_url, server, task = await run_uvicorn_in_task(app)

    try:
        http1 = await _collect_transport_response(
            base_url=base_url,
            transport="h1",
            use_http2=False,
        )
        http2 = await _collect_transport_response(
            base_url=base_url,
            transport="h2",
            use_http2=True,
        )
        http3 = await _collect_transport_response(
            base_url=base_url,
            transport="h3",
            use_http2=False,
        )

        assert http1["rest"]["status"] == 200
        assert http2["rest"]["status"] == 200
        assert http3["rest"]["status"] == 200

        assert http1["jsonrpc"]["status"] == 200
        assert http2["jsonrpc"]["status"] == 200
        assert http3["jsonrpc"]["status"] == 200

        assert http1["jsonrpc"]["body"]["result"]["name"] == "h1-widget"
        assert http2["jsonrpc"]["body"]["result"]["name"] == "h2-widget"
        assert http3["jsonrpc"]["body"]["result"]["name"] == "h3-widget"
    finally:
        await stop_uvicorn_server(server, task)

import asyncio
import json

import pytest

from swarmauri_core.transports.enums import Feature
from swarmauri_transport_wsjsonrpcmux import (
    WsJsonrpcMuxTransport,
    WsJsonrpcTransport,
)


class _FakeWebSocket:
    def __init__(self) -> None:
        self.sent: asyncio.Queue[str] = asyncio.Queue()
        self.received: asyncio.Queue[str | None] = asyncio.Queue()

    async def send(self, message: str) -> None:
        await self.sent.put(message)

    async def close(self) -> None:
        await self.received.put(None)

    def __aiter__(self):
        return self

    async def __anext__(self) -> str:
        message = await self.received.get()
        if message is None:
            raise StopAsyncIteration
        return message


def test_compatibility_alias_does_not_advertise_multiplexing() -> None:
    assert WsJsonrpcMuxTransport is WsJsonrpcTransport
    assert Feature.MULTIPLEX not in WsJsonrpcTransport().supports().features


@pytest.mark.asyncio
async def test_concurrent_calls_are_correlated_by_jsonrpc_id() -> None:
    transport = WsJsonrpcTransport()
    socket = _FakeWebSocket()
    transport._ws = socket
    transport._receiver_task = asyncio.create_task(transport._receive_loop())

    first = asyncio.create_task(transport.call("echo", "first"))
    second = asyncio.create_task(transport.call("echo", "second"))
    requests = [json.loads(await socket.sent.get()) for _ in range(2)]

    for request in reversed(requests):
        await socket.received.put(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": request["id"],
                    "result": request["params"],
                }
            )
        )

    assert await first == "first"
    assert await second == "second"
    await transport._close_client()

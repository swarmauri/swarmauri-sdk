import asyncio

import pytest
from swarmauri_transport_tcpunicast import TCPUnicast

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


async def test_disconnected_send_and_receive_fail():
    transport = TCPUnicast()
    with pytest.raises(RuntimeError, match="not connected"):
        await transport.send("peer", b"hello")
    with pytest.raises(RuntimeError, match="not connected"):
        await transport.recv()


async def test_loopback_roundtrip_and_server_cleanup():
    server = TCPUnicast()
    client = TCPUnicast()
    async with server.server(host="127.0.0.1", port=0):
        port = server._server.sockets[0].getsockname()[1]
        async with client.client(host="127.0.0.1", port=port):
            await client.send("server", b"hello", timeout=2)
            peers = server.accept()
            reader, writer = await asyncio.wait_for(anext(peers), timeout=2)
            assert reader is server._reader
            assert writer is server._writer
            await peers.aclose()
            assert await server.recv(timeout=2) == b"hello"
            await server.send("client", b"world", timeout=2)
            assert await client.recv(timeout=2) == b"world"
        assert client._writer is None
    assert server._server is None
    assert server._writer is None


async def test_accept_requires_running_server():
    peers = TCPUnicast().accept()
    with pytest.raises(RuntimeError, match="server not started"):
        await anext(peers)

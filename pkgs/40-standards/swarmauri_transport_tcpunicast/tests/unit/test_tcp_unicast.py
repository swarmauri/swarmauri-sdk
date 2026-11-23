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


async def test_shutdown_wakes_all_pending_accept_iterators():
    server = TCPUnicast()
    async with server.server(host="127.0.0.1", port=0):
        tasks = [asyncio.create_task(anext(server.accept())) for _ in range(3)]
        await asyncio.sleep(0)
        assert all(not task.done() for task in tasks)
    results = await asyncio.wait_for(
        asyncio.gather(*tasks, return_exceptions=True), 2
    )
    assert all(isinstance(result, StopAsyncIteration) for result in results)


async def test_cancelled_accept_does_not_block_other_waiters():
    server = TCPUnicast()
    async with server.server(host="127.0.0.1", port=0):
        cancelled = asyncio.create_task(anext(server.accept()))
        survivor = asyncio.create_task(anext(server.accept()))
        await asyncio.sleep(0)
        cancelled.cancel()
        with pytest.raises(asyncio.CancelledError):
            await cancelled
    with pytest.raises(StopAsyncIteration):
        await asyncio.wait_for(survivor, 2)


async def test_old_iterator_does_not_accept_from_restarted_server():
    server = TCPUnicast()
    client = TCPUnicast()
    async with server.server(host="127.0.0.1", port=0):
        port = server._server.sockets[0].getsockname()[1]
        async with client.client(host="127.0.0.1", port=port):
            old = server.accept()
            await asyncio.wait_for(anext(old), 2)
    async with server.server(host="127.0.0.1", port=0):
        port = server._server.sockets[0].getsockname()[1]
        async with client.client(host="127.0.0.1", port=port):
            with pytest.raises(StopAsyncIteration):
                await asyncio.wait_for(anext(old), 2)
            fresh = server.accept()
            reader, _ = await asyncio.wait_for(anext(fresh), 2)
            await client.send("server", b"new session", timeout=2)
            assert await asyncio.wait_for(reader.read(32), 2) == b"new session"
            await fresh.aclose()


async def test_shutdown_closes_queued_connection():
    server = TCPUnicast()
    async with server.server(host="127.0.0.1", port=0):
        port = server._server.sockets[0].getsockname()[1]
        reader, writer = await asyncio.open_connection("127.0.0.1", port)

        async def accepted():
            while server._writer is None:
                await asyncio.sleep(0)

        await asyncio.wait_for(accepted(), 2)
        assert server._accept_queue.qsize() == 1
    try:
        assert await asyncio.wait_for(reader.read(1), 2) == b""
        with pytest.raises(RuntimeError, match="server not started"):
            # Fresh iterators still reject an unstarted server.
            old = server.accept()
            await anext(old)
    finally:
        writer.close()
        await writer.wait_closed()

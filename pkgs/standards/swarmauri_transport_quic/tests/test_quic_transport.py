import asyncio
import socket

import pytest

from swarmauri_transport_quic import QuicTransport


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.mark.asyncio
async def test_quic_transport_unicast_and_multiplex_round_trip() -> None:
    port = _find_free_port()
    server = QuicTransport()
    client = QuicTransport()

    async with server.server(host="127.0.0.1", port=port):
        async with client.client(host="127.0.0.1", port=port):
            await asyncio.sleep(0.05)

            await client.send("server", b"hello")
            message = await asyncio.wait_for(server.recv(timeout=1), 1)
            assert message == b"hello"

            handle = await client.open_channel()
            await client.send_on(handle, b"stream")
            stream_data = await asyncio.wait_for(server.recv_on(handle, timeout=1), 1)
            assert stream_data == b"stream"

            await server.send_on(handle, b"reply")
            reply = await asyncio.wait_for(client.recv_on(handle, timeout=1), 1)
            assert reply == b"reply"

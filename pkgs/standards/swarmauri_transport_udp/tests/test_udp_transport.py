import asyncio
import socket

import pytest

from swarmauri_transport_udp import UdpTransport


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.mark.asyncio
async def test_udp_transport_unicast_round_trip() -> None:
    port = _find_free_port()
    server = UdpTransport(bind=f"127.0.0.1:{port}")
    client = UdpTransport()

    async with server.server():
        async with client.client():
            await client.send(f"127.0.0.1:{port}", b"udp")
            message = await asyncio.wait_for(server.recv(timeout=1), 1)

    assert message == b"udp"

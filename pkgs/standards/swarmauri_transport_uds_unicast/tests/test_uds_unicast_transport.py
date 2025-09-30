import asyncio
import pytest

from swarmauri_transport_uds_unicast import UdsUnicastTransport


@pytest.mark.asyncio
async def test_uds_unicast_round_trip(tmp_path) -> None:
    path = tmp_path / "uds.sock"
    server = UdsUnicastTransport(str(path))
    client = UdsUnicastTransport(str(path))

    async with server.server():
        async with client.client():
            for _ in range(50):
                if server._writer is not None:  # type: ignore[attr-defined]
                    break
                await asyncio.sleep(0.01)
            else:
                pytest.fail("server did not accept connection")

            await client.send("server", b"ping")
            data = await asyncio.wait_for(server.recv(timeout=1), 1)
            assert data == b"ping"

            await server.send("client", b"pong")
            echo = await asyncio.wait_for(client.recv(timeout=1), 1)
            assert echo == b"pong"

    assert not path.exists()

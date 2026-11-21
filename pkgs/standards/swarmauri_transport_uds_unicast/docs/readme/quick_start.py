import asyncio
from swarmauri_transport_uds_unicast import UdsUnicastTransport

SOCKET_PATH = "/tmp/swm-uds.sock"


async def main() -> None:
    server = UdsUnicastTransport(SOCKET_PATH)

    async def run_server():
        async with server.server():
            data = await server.recv()
            await server.send("peer", b"echo:" + data)

    async def run_client():
        client = UdsUnicastTransport(SOCKET_PATH)
        async with client.client():
            await client.send("server", b"ping")
            response = await client.recv()
            print(response.decode())

    await asyncio.gather(run_server(), run_client())


asyncio.run(main())

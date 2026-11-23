import asyncio
from swarmauri_transport_sshtunnel import SSHTunnelTransport


async def tunnel() -> None:
    transport = SSHTunnelTransport("bastion", "intranet.local", 5432)
    async with transport.client():
        await transport.send("db", b"hello")
        reply = await transport.recv()
        print(reply)


asyncio.run(tunnel())

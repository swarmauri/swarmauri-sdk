import asyncio
from swarmauri_transport_udp import UdpTransport


async def main():
    server = UdpTransport(bind="0.0.0.0:5000", multicast_groups=["239.1.2.3"])

    async def run_server():
        async with server.server():
            message = await server.recv()
            await server.broadcast(b"broadcast:" + message)
            await server.multicast(["239.1.2.3:5000"], b"multicast:" + message)

    async def run_client():
        client = UdpTransport()
        async with client.client():
            await client.send("127.0.0.1:5000", b"udp-ping")
            reply = await client.recv()
            print(reply.decode())

    await asyncio.gather(run_server(), run_client())


asyncio.run(main())

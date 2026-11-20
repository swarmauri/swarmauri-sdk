import asyncio
from swarmauri_transport_tcpunicast import TCPUnicast


async def echo_server() -> None:
    transport = TCPUnicast()
    async with transport.server(host="0.0.0.0", port=9999):
        data = await transport.recv()
        await transport.send("client", data)


asyncio.run(echo_server())

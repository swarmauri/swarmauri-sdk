import asyncio
from swarmauri_transport_sseoutbound import SSEOutboundTransport


async def main() -> None:
    transport = SSEOutboundTransport()
    async with transport.server(host="0.0.0.0", port=8082):
        await transport.broadcast(b"hello, world!")


asyncio.run(main())

import asyncio
from swarmauri_transport_h2mux import H2MuxTransport


async def main() -> None:
    mux = H2MuxTransport()
    async with mux.client(host="example.com", port=443):
        channel = await mux.open_channel()
        await mux.send_on(channel, b"ping")
        payload = await mux.recv_on(channel)
        print(payload)


asyncio.run(main())

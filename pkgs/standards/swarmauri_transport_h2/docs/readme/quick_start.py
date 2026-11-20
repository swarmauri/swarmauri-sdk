import asyncio
from swarmauri_transport_h2 import H2Transport


async def run_request() -> None:
    transport = H2Transport()
    async with transport.client(host="example.com", port=443):
        status, headers, body = await transport.request("GET", "/")
        print(status, headers, body)


asyncio.run(run_request())

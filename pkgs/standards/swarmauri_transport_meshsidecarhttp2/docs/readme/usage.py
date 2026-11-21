import asyncio
from swarmauri_transport_meshsidecarhttp2 import MeshSidecarHttp2


async def call_sidecar() -> None:
    transport = MeshSidecarHttp2()
    async with transport.client(host="127.0.0.1", port=15001):
        await asyncio.sleep(1)  # interact with the sidecar connection here


asyncio.run(call_sidecar())

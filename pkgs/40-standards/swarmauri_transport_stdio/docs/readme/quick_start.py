import asyncio
from swarmauri_transport_stdio import StdioTransport


async def run_tool() -> None:
    transport = StdioTransport(["python", "script.py"])
    async with transport.client():
        await transport.send("tool", b"input\n")
        print(await transport.recv())


asyncio.run(run_tool())

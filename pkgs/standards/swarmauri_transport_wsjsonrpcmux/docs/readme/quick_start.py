import asyncio
from swarmauri_transport_wsjsonrpcmux import WsJsonrpcTransport


async def handler(method: str, params):
    if method == "echo":
        return params
    raise ValueError("unknown method")


async def main() -> None:
    transport = WsJsonrpcTransport()
    transport.set_rpc_handler(handler)
    async with transport.server(host="127.0.0.1", port=8765):
        await asyncio.sleep(1)


asyncio.run(main())

import asyncio
from fastapi import FastAPI
from swarmauri_transport_asgi import ASGITransport

api = FastAPI()


@api.get("/ping")
async def ping() -> dict[str, str]:
    return {"message": "pong"}


async def main() -> None:
    transport = ASGITransport(app=api)
    async with transport.server(host="0.0.0.0", port=8000):
        await asyncio.Event().wait()


asyncio.run(main())

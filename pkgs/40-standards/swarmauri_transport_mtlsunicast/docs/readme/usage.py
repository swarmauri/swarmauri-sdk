import asyncio
import ssl
from swarmauri_transport_mtlsunicast import MTLSUnicast


async def secure_client() -> None:
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.load_cert_chain("client.crt", "client.key")
    ctx.load_verify_locations("ca.crt")

    transport = MTLSUnicast(ctx)
    async with transport.client(host="secure.example", port=9443):
        await transport.send("server", b"hello")
        reply = await transport.recv()
        print(reply)


asyncio.run(secure_client())

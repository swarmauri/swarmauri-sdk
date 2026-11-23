import asyncio
import os
import ssl
from swarmauri_transport_tls_unicast import TlsUnicastTransport


async def main():
    port = int(os.environ.get("TLS_EXAMPLE_PORT", "8443"))
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain("server.pem", "server.key")
    client_context = ssl.create_default_context(cafile="ca.pem")
    ready = asyncio.Event()
    transport = TlsUnicastTransport(server_context)

    async def serve():
        async with transport.server(host="127.0.0.1", port=port):
            ready.set()
            async for reader, writer in transport.accept():
                request = await transport.recv(timeout=5)
                await transport.send("peer", b"tls:" + request, timeout=5)
                writer.close()
                await writer.wait_closed()
                break

    async def request():
        await ready.wait()
        client = TlsUnicastTransport(client_context, sni="localhost")
        async with client.client(host="127.0.0.1", port=port):
            await client.send("server", b"hello", timeout=5)
            assert await client.recv(timeout=5) == b"tls:hello"

    await asyncio.gather(serve(), request())


asyncio.run(main())

import asyncio
from swarmauri_transport_quic import QuicTransport


async def main():
    server = QuicTransport(cert="srv.pem", key="srv.key")
    client = QuicTransport(server_name="localhost")

    async def run_server():
        async with server.server(host="0.0.0.0", port=4433):
            channel = await server.open_channel()
            await server.send_on(channel, b"welcome")
            data = await server.recv_on(channel)
            await server.send_on(channel, b"ack:" + data)
            await server.close_channel(channel)

    async def run_client():
        async with client.client(host="127.0.0.1", port=4433):
            channel = await client.open_channel()
            await client.send_on(channel, b"hi-quic")
            response = await client.recv_on(channel)
            print(response.decode())
            await client.close_channel(channel)

    await asyncio.gather(run_server(), run_client())


asyncio.run(main())

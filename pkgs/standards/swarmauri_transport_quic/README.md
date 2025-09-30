# Swarmauri QUIC Transport

![Transport Icon](https://img.shields.io/badge/transport-quic-4B8BF4.svg)
![Multiplex](https://img.shields.io/badge/feature-multiplexing-9B59B6.svg)
![Lifecycle](https://img.shields.io/badge/lifecycle-async%20contexts-1E90FF.svg)

The **Swarmauri QUIC Transport** outlines a multiplexed, encrypted transport
based on QUIC. It shares the unified lifecycle helpers so that future
implementations can expose `.server(...)`, `.client(...)`, and channel-aware
APIs directly on the transport instance.

> **Note**: This package currently ships a skeleton with `NotImplementedError`
> placeholders so downstream teams can integrate their preferred QUIC stack.

## Installation

### Using `uv`

```bash
uv add --directory pkgs/standards/swarmauri_transport_quic swarmauri_transport_quic
```

### Using `pip`

```bash
pip install swarmauri_transport_quic
```

## Usage

The example below demonstrates the lifecycle of a QUIC transport once the
implementation details are filled in.

```python
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
```

Replace the placeholders with concrete QUIC operations once your chosen
library is integrated.

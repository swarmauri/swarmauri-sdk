# Swarmauri UDP Transport

![Transport Icon](https://img.shields.io/badge/transport-udp_family-4B8BF4.svg)
![Casts](https://img.shields.io/badge/casts-unicast%2Fbroadcast%2Fmulticast%2Fanycast-FF8C00.svg)
![Lifecycle](https://img.shields.io/badge/lifecycle-async%20contexts-1E90FF.svg)

The **Swarmauri UDP Transport** provides a datagram-oriented transport with
unicast, broadcast, multicast, and anycast semantics. It plugs into the unified
transport lifecycle to guarantee capability-safe server and client contexts.

## Installation

### Using `uv`

```bash
uv add --directory pkgs/standards/swarmauri_transport_udp swarmauri_transport_udp
```

### Using `pip`

```bash
pip install swarmauri_transport_udp
```

## Usage

Below is a simple example that sends a message to a UDP server, which then
rebroadcasts the payload.

```python
import asyncio
from swarmauri_transport_udp import UdpTransport

async def main():
    server = UdpTransport(bind="0.0.0.0:5000", multicast_groups=["239.1.2.3"])

    async def run_server():
        async with server.server():
            message = await server.recv()
            await server.broadcast(b"broadcast:" + message)
            await server.multicast(["239.1.2.3:5000"], b"multicast:" + message)

    async def run_client():
        client = UdpTransport()
        async with client.client():
            await client.send("127.0.0.1:5000", b"udp-ping")
            reply = await client.recv()
            print(reply.decode())

    await asyncio.gather(run_server(), run_client())

asyncio.run(main())
```

Adjust the `bind` address and multicast groups to suit your environment. The
transport leaves socket configuration open so you can customize TTL, reuse,
and other behaviors as needed.

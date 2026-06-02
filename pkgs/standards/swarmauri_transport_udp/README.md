![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_udp/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_udp/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_udp/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_udp.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_udp/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_udp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_udp" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_udp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_udp?label=swarmauri_transport_udp&color=green" alt="PyPI - swarmauri_transport_udp"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

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



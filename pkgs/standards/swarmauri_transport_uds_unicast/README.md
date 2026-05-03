![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_uds_unicast/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_uds_unicast/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_uds_unicast/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_uds_unicast.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_uds_unicast/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_transport_uds_unicast" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_uds_unicast/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_uds_unicast" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_uds_unicast/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_uds_unicast?label=swarmauri_transport_uds_unicast&color=green" alt="PyPI - swarmauri_transport_uds_unicast"/></a>
</p>
---

# Swarmauri UDS Unicast Transport

![Transport Icon](https://img.shields.io/badge/transport-uds_unicast-4B8BF4.svg)
![Lifecycle](https://img.shields.io/badge/lifecycle-async%20contexts-1E90FF.svg)
![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)

The **Swarmauri UDS Unicast Transport** offers reliable, ordered, local-only
communication over Unix domain sockets. It embraces the unified transport
lifecycle so the server and client contexts are created directly from the
transport instance (`.server(...)` / `.client(...)`).

## Installation

### Using `uv`

```bash
uv add --directory pkgs/standards/swarmauri_transport_uds_unicast swarmauri_transport_uds_unicast
```

### Using `pip`

```bash
pip install swarmauri_transport_uds_unicast
```

## Usage

The example below demonstrates setting up a server and client that echo
messages over a Unix domain socket path.

```python
import asyncio
from swarmauri_transport_uds_unicast import UdsUnicastTransport

SOCKET_PATH = "/tmp/swm-uds.sock"

async def main() -> None:
    server = UdsUnicastTransport(SOCKET_PATH)

    async def run_server():
        async with server.server():
            data = await server.recv()
            await server.send("peer", b"echo:" + data)

    async def run_client():
        client = UdsUnicastTransport(SOCKET_PATH)
        async with client.client():
            await client.send("server", b"ping")
            response = await client.recv()
            print(response.decode())

    await asyncio.gather(run_server(), run_client())

asyncio.run(main())
```

This transport is ideal for same-host communication where low latency and
security isolation are required.

![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_sseoutbound/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_sseoutbound/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_sseoutbound/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_sseoutbound.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_sseoutbound/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_sseoutbound/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_sseoutbound" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_sseoutbound/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_sseoutbound?label=swarmauri_transport_sseoutbound&color=green" alt="PyPI - swarmauri_transport_sseoutbound"/></a>
</p>

# Swarmauri Transport â€“ Server-Sent Events

`swarmauri-transport-sseoutbound` hosts a lightweight SSE endpoint for broadcasting real-time updates to browsers or other streaming clients.

## Installation

### Using `uv`

```bash
uv pip install swarmauri-transport-sseoutbound --index-url https://pypi.org/simple
```

### Using `pip`

```bash
pip install swarmauri-transport-sseoutbound
```

## Usage

```python
import asyncio
from swarmauri_transport_sseoutbound import SSEOutboundTransport

async def main() -> None:
    transport = SSEOutboundTransport()
    async with transport.server(host="0.0.0.0", port=8082):
        await transport.broadcast(b"hello, world!")

asyncio.run(main())
```

Attach your own event loop or scheduler to push updates whenever your agents produce new data.

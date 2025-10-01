![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-transport-sseoutbound/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-transport-sseoutbound" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_sseoutbound/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_sseoutbound.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-sseoutbound/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-transport-sseoutbound" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-sseoutbound/">
        <img src="https://img.shields.io/pypi/l/swarmauri-transport-sseoutbound" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-sseoutbound/">
        <img src="https://img.shields.io/pypi/v/swarmauri-transport-sseoutbound?label=swarmauri-transport-sseoutbound&color=green" alt="PyPI - swarmauri-transport-sseoutbound"/>
    </a>
</p>

---

# Swarmauri Transport – Server-Sent Events

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

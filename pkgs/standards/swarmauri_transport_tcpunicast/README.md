![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_tcpunicast/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_tcpunicast/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_tcpunicast/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_tcpunicast.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_tcpunicast/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_transport_tcpunicast" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_tcpunicast/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_tcpunicast" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_tcpunicast/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_tcpunicast?label=swarmauri_transport_tcpunicast&color=green" alt="PyPI - swarmauri_transport_tcpunicast"/></a>
</p>
---

# Swarmauri Transport â€“ TCP Unicast

`swarmauri-transport-tcpunicast` offers a lightweight TCP harness for prototyping Swarmauri agents.

## Installation

### Using `uv`

```bash
uv pip install swarmauri-transport-tcpunicast --index-url https://pypi.org/simple
```

### Using `pip`

```bash
pip install swarmauri-transport-tcpunicast
```

## Usage

```python
import asyncio
from swarmauri_transport_tcpunicast import TCPUnicast

async def echo_server() -> None:
    transport = TCPUnicast()
    async with transport.server(host="0.0.0.0", port=9999):
        data = await transport.recv()
        await transport.send("client", data)

asyncio.run(echo_server())
```

Swap in your own handlers to forward traffic, feed LLM pipelines, or compose with other Swarmauri transports.

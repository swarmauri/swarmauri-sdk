![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_tcpunicast/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_tcpunicast/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_tcpunicast/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_tcpunicast.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_tcpunicast/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_tcpunicast/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_tcpunicast" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_tcpunicast/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_tcpunicast?label=swarmauri_transport_tcpunicast&color=green" alt="PyPI - swarmauri_transport_tcpunicast"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Transport TCP Unicast

`swarmauri-transport-tcpunicast` offers a lightweight TCP harness for prototyping Swarmauri agents.

## Features

- Async TCP client and server contexts for one active peer.
- Reliable, ordered byte streams with configurable send and receive timeouts.
- Swarmauri transport capability discovery and lifecycle helpers.
- Support for Python 3.10 through 3.12.

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



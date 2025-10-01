![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-transport-tcpunicast/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-transport-tcpunicast" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_tcpunicast/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_tcpunicast.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-tcpunicast/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-transport-tcpunicast" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-tcpunicast/">
        <img src="https://img.shields.io/pypi/l/swarmauri-transport-tcpunicast" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-tcpunicast/">
        <img src="https://img.shields.io/pypi/v/swarmauri-transport-tcpunicast?label=swarmauri-transport-tcpunicast&color=green" alt="PyPI - swarmauri-transport-tcpunicast"/>
    </a>
</p>

---

# Swarmauri Transport – TCP Unicast

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

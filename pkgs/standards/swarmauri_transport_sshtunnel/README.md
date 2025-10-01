![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-transport-sshtunnel/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-transport-sshtunnel" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_sshtunnel/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_sshtunnel.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-sshtunnel/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-transport-sshtunnel" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-sshtunnel/">
        <img src="https://img.shields.io/pypi/l/swarmauri-transport-sshtunnel" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-sshtunnel/">
        <img src="https://img.shields.io/pypi/v/swarmauri-transport-sshtunnel?label=swarmauri-transport-sshtunnel&color=green" alt="PyPI - swarmauri-transport-sshtunnel"/>
    </a>
</p>

---

# Swarmauri Transport – SSH Tunnel

`swarmauri-transport-sshtunnel` wraps `ssh -W` to forward TCP streams through bastion hosts while keeping the Swarmauri transport API.

## Installation

### Using `uv`

```bash
uv pip install swarmauri-transport-sshtunnel --index-url https://pypi.org/simple
```

### Using `pip`

```bash
pip install swarmauri-transport-sshtunnel
```

## Usage

```python
import asyncio
from swarmauri_transport_sshtunnel import SSHTunnelTransport

async def tunnel() -> None:
    transport = SSHTunnelTransport("bastion", "intranet.local", 5432)
    async with transport.client():
        await transport.send("db", b"hello")
        reply = await transport.recv()
        print(reply)

asyncio.run(tunnel())
```

Ensure SSH credentials, host keys, and jump host policies are configured on the machine executing the transport.

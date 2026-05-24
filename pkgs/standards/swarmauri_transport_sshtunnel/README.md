![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_sshtunnel/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_sshtunnel/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_sshtunnel/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_sshtunnel.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_sshtunnel/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_sshtunnel/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_sshtunnel" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_sshtunnel/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_sshtunnel?label=swarmauri_transport_sshtunnel&color=green" alt="PyPI - swarmauri_transport_sshtunnel"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Transport â€“ SSH Tunnel

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



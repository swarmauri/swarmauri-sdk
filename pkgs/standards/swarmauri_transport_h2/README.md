![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_h2/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_h2/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_h2/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_h2.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_h2/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_h2/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_h2" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_h2/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_h2?label=swarmauri_transport_h2&color=green" alt="PyPI - swarmauri_transport_h2"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Transport ? HTTP/2 Adapter

`swarmauri-transport-h2` layers HTTP semantics on top of the reusable `H2MuxTransport`, giving you request/response helpers while preserving multiplexed channel control.

## Installation

### Using `uv`

```bash
uv pip install swarmauri-transport-h2 --index-url https://pypi.org/simple
```

### Using `pip`

```bash
pip install swarmauri-transport-h2
```

## Usage

```python
import asyncio
from swarmauri_transport_h2 import H2Transport

async def run_request() -> None:
    transport = H2Transport()
    async with transport.client(host="example.com", port=443):
        status, headers, body = await transport.request("GET", "/")
        print(status, headers, body)

asyncio.run(run_request())
```

The adapter lets you reuse a single HTTP/2 connection for multiple requests, plug in custom channel management, or proxy calls to Swarmauri agents.



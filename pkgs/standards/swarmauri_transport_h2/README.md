![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-transport-h2/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-transport-h2" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_h2/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_h2.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-h2/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-transport-h2" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-h2/">
        <img src="https://img.shields.io/pypi/l/swarmauri-transport-h2" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-h2/">
        <img src="https://img.shields.io/pypi/v/swarmauri-transport-h2?label=swarmauri-transport-h2&color=green" alt="PyPI - swarmauri-transport-h2"/>
    </a>
</p>

---

# Swarmauri Transport – HTTP/2 Adapter

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

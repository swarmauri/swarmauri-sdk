![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_h2mux/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_h2mux/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_h2mux/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_h2mux.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_h2mux/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_transport_h2mux" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_h2mux/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_h2mux" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_h2mux/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_h2mux?label=swarmauri_transport_h2mux&color=green" alt="PyPI - swarmauri_transport_h2mux"/></a>
</p>
---

# Swarmauri Transport â€“ H2 Multiplexer

`swarmauri-transport-h2mux` exposes raw HTTP/2 stream management to Swarmauri transports. It handles connection setup, stream lifecycle, and data flow so higher-level protocols can be layered on top.

## Installation

### Using `uv`

```bash
uv pip install swarmauri-transport-h2mux --index-url https://pypi.org/simple
```

### Using `pip`

```bash
pip install swarmauri-transport-h2mux
```

## Usage

```python
import asyncio
from swarmauri_transport_h2mux import H2MuxTransport

async def main() -> None:
    mux = H2MuxTransport()
    async with mux.client(host="example.com", port=443):
        channel = await mux.open_channel()
        await mux.send_on(channel, b"ping")
        payload = await mux.recv_on(channel)
        print(payload)

asyncio.run(main())
```

Use the multiplexer when you need direct stream controlâ€”for example to build custom RPC layers or bridge Swarmauri agents over HTTP/2 without binding to REST semantics.

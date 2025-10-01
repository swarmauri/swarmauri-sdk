![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-transport-h2mux/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-transport-h2mux" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_h2mux/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_h2mux.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-h2mux/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-transport-h2mux" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-h2mux/">
        <img src="https://img.shields.io/pypi/l/swarmauri-transport-h2mux" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-h2mux/">
        <img src="https://img.shields.io/pypi/v/swarmauri-transport-h2mux?label=swarmauri-transport-h2mux&color=green" alt="PyPI - swarmauri-transport-h2mux"/>
    </a>
</p>

---

# Swarmauri Transport – H2 Multiplexer

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

Use the multiplexer when you need direct stream control—for example to build custom RPC layers or bridge Swarmauri agents over HTTP/2 without binding to REST semantics.

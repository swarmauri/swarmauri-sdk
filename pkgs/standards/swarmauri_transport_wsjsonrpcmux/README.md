![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-transport-wsjsonrpcmux/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-transport-wsjsonrpcmux" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_wsjsonrpcmux/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_wsjsonrpcmux.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-wsjsonrpcmux/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-transport-wsjsonrpcmux" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-wsjsonrpcmux/">
        <img src="https://img.shields.io/pypi/l/swarmauri-transport-wsjsonrpcmux" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-wsjsonrpcmux/">
        <img src="https://img.shields.io/pypi/v/swarmauri-transport-wsjsonrpcmux?label=swarmauri-transport-wsjsonrpcmux&color=green" alt="PyPI - swarmauri-transport-wsjsonrpcmux"/>
    </a>
</p>

---

# Swarmauri Transport – WebSocket JSON-RPC

`swarmauri-transport-wsjsonrpcmux` provides a JSON-RPC 2.0 dispatcher over WebSockets for browser-friendly agent communication.

## Installation

### Using `uv`

```bash
uv pip install swarmauri-transport-wsjsonrpcmux --index-url https://pypi.org/simple
```

### Using `pip`

```bash
pip install swarmauri-transport-wsjsonrpcmux
```

## Usage

```python
import asyncio
from swarmauri_transport_wsjsonrpcmux import WsJsonrpcMuxTransport

async def handler(method: str, params):
    if method == "echo":
        return params
    raise ValueError("unknown method")

async def main() -> None:
    transport = WsJsonrpcMuxTransport()
    transport.set_rpc_handler(handler)
    async with transport.server(host="127.0.0.1", port=8765):
        await asyncio.sleep(1)

asyncio.run(main())
```

Pair the server with a client created via `WsJsonrpcMuxTransport().client(...)` and `call(...)` to complete the RPC loop.

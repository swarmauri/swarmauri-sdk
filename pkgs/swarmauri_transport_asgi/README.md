![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-transport-asgi/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-transport-asgi" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_asgi/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_asgi.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-asgi/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-transport-asgi" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-asgi/">
        <img src="https://img.shields.io/pypi/l/swarmauri-transport-asgi" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-asgi/">
        <img src="https://img.shields.io/pypi/v/swarmauri-transport-asgi?label=swarmauri-transport-asgi&color=green" alt="PyPI - swarmauri-transport-asgi"/>
    </a>
</p>

---

# Swarmauri Transport – ASGI Server

`swarmauri-transport-asgi` boots an in-process [Uvicorn](https://www.uvicorn.org/) server so transports can expose ASGI applications without leaving the Swarmauri runtime. Use it when you need to mount FastAPI, Starlette, or other ASGI-compatible apps alongside agents.

## Installation

### Using `uv`

```bash
uv pip install swarmauri-transport-asgi --index-url https://pypi.org/simple
```

### Using `pip`

```bash
pip install swarmauri-transport-asgi
```

## Usage

```python
import asyncio
from fastapi import FastAPI
from swarmauri_transport_asgi import ASGITransport

api = FastAPI()

@api.get("/ping")
async def ping() -> dict[str, str]:
    return {"message": "pong"}

async def main() -> None:
    transport = ASGITransport(app=api)
    async with transport.server(host="0.0.0.0", port=8000):
        await asyncio.Event().wait()

asyncio.run(main())
```

Configure Uvicorn parameters such as TLS context or worker count through the `server(...)` context manager arguments.

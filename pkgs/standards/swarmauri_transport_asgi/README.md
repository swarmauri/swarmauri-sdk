![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_asgi/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_asgi/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_asgi/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_asgi.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_asgi/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_asgi/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_asgi" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_asgi/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_asgi?label=swarmauri_transport_asgi&color=green" alt="PyPI - swarmauri_transport_asgi"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Transport â€“ ASGI Server

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



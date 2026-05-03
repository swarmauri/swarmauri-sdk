![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri-transport-mtlsunicast/">
        <img src="https://static.pepy.tech/badge/swarmauri-transport-mtlsunicast/month" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_mtlsunicast/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_transport_mtlsunicast.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-mtlsunicast/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-transport-mtlsunicast" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-mtlsunicast/">
        <img src="https://img.shields.io/pypi/l/swarmauri-transport-mtlsunicast" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-transport-mtlsunicast/">
        <img src="https://img.shields.io/pypi/v/swarmauri-transport-mtlsunicast?label=swarmauri-transport-mtlsunicast&color=green" alt="PyPI - swarmauri-transport-mtlsunicast"/>
    </a>
</p>

---

# Swarmauri Transport â€“ Mutual TLS Unicast

`swarmauri-transport-mtlsunicast` scaffolds mutually authenticated TLS channels for Swarmauri agents.

## Installation

### Using `uv`

```bash
uv pip install swarmauri-transport-mtlsunicast --index-url https://pypi.org/simple
```

### Using `pip`

```bash
pip install swarmauri-transport-mtlsunicast
```

## Usage

```python
import asyncio
import ssl
from swarmauri_transport_mtlsunicast import MTLSUnicast

async def secure_client() -> None:
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.load_cert_chain("client.crt", "client.key")
    ctx.load_verify_locations("ca.crt")

    transport = MTLSUnicast(ctx)
    async with transport.client(host="secure.example", port=9443):
        await transport.send("server", b"hello")
        reply = await transport.recv()
        print(reply)

asyncio.run(secure_client())
```

Customize the SSL context for your environmentâ€”pin certificates, enable ALPN, or integrate with service mesh trust stores.

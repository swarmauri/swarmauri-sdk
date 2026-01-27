![Tigrbl Logo](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/tigrbl_api_hpks/">
        <img src="https://img.shields.io/pypi/dm/tigrbl_api_hpks" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/tigrbl_api_hpks/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/tigrbl_api_hpks.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_api_hpks/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_api_hpks" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_api_hpks/">
        <img src="https://img.shields.io/pypi/l/tigrbl_api_hpks" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_api_hpks/">
        <img src="https://img.shields.io/pypi/v/tigrbl_api_hpks?label=tigrbl_api_hpks&color=green" alt="PyPI - tigrbl_api_hpks"/></a>
</p>

---

# Tigrbl API HPKS 🔐

> High-trust OpenPGP keyserver APIs that embrace the HPKS v2 specification while preserving legacy HKP compatibility, powered by the Tigrbl application engine.

## ✨ Features

- 🔄 **Dual-protocol support** – serves both legacy `/pks/lookup` flows and HPKS v2 JSON/binary routes with consistent persistence.
- 🧩 **Merge-aware storage** – idempotent upserts normalize fingerprints, union metadata, and track revocation state without losing history.
- 📦 **Single source of truth** – admin CRUD and public HPKS endpoints share the same `openpgp_keys` table and Tigrbl handlers.
- 🛡️ **Spec-aligned responses** – machine-readable index output, binary bundle delivery, and required CORS headers baked in.
- ⚙️ **Composable operations** – `@op_ctx` powered helpers expose reusable alias handlers for `/pks` workflows.

## 📦 Installation

### Using `uv`

```bash
uv add tigrbl_api_hpks
```

### Using `pip`

```bash
pip install tigrbl_api_hpks
```

## 🚀 Quick Start

```python
import asyncio
from httpx import ASGITransport, AsyncClient

from tigrbl_api_hpks import app


async def bootstrap():
    await app.initialize()  # create in-memory tables

    # Submit an ASCII-armored key bundle via the legacy endpoint
    armored_blob = """-----BEGIN PGP PUBLIC KEY BLOCK-----\n...\n-----END PGP PUBLIC KEY BLOCK-----"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        resp = await client.post(
            "/pks/add",
            data={"keytext": armored_blob},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()

        # Lookup via HPKS v2 JSON index
        lookup = await client.get("/pks/v2/index/example.com")
        print(lookup.json())


asyncio.run(bootstrap())
```

## 🧪 Testing

Run the package test suite in isolation:

```bash
uv run --package tigrbl_api_hpks --directory pkgs/community/tigrbl_api_hpks pytest
```

## 📄 License

This project is licensed under the terms of the [Apache 2.0](LICENSE) license.

# tigrbl_engine_membloom

![Tigrbl Branding](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

![PyPI - Downloads](https://img.shields.io/pypi/dm/tigrbl_engine_membloom)
![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg?label=hits)
![Python Versions](https://img.shields.io/pypi/pyversions/tigrbl_engine_membloom)
![License](https://img.shields.io/pypi/l/tigrbl_engine_membloom)
![Version](https://img.shields.io/pypi/v/tigrbl_engine_membloom)

Process-local Bloom filter engine for Tigrbl. This plugin provides probabilistic set-membership operations with stable hashing and optional approximate TTL via rotating Bloom windows.

## Features

- Stable `blake2b` hashing with double hashing index generation.
- Configurable expected capacity and false-positive rate.
- Optional TTL-like behavior using a ring of Bloom filters.
- Sync and async session wrappers.
- Plugin registration through the `tigrbl.engine` entry-point group.

## Installation

### uv

```bash
uv add tigrbl_engine_membloom
```

### pip

```bash
pip install tigrbl_engine_membloom
```

## Usage

```python
from tigrbl import engine_ctx

@engine_ctx({
    "kind": "membloom",
    "capacity": 1_000_000,
    "fp_rate": 1e-4,
    "namespace": "idempotency",
    "windows": 6,
    "window_seconds": 10.0,
})
def handle(db, key: str):
    return {"fresh": db.add_if_absent(key)}
```

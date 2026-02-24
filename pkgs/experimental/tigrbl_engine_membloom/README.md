# tigrbl_engine_membloom

![Tigrbl](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

![PyPI - Downloads](https://img.shields.io/pypi/dm/tigrbl_engine_membloom)
![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)
![Python Versions](https://img.shields.io/pypi/pyversions/tigrbl_engine_membloom)
![License](https://img.shields.io/pypi/l/tigrbl_engine_membloom)
![Version](https://img.shields.io/pypi/v/tigrbl_engine_membloom)

Process-local Bloom filter engine plugin for Tigrbl with stable hashing and optional rotating-window TTL behavior.

## Features

- Bloom membership checks with configurable capacity and false-positive target.
- Deterministic BLAKE2b-based double hashing.
- Optional approximate TTL via rotating window ring filters.
- Sync and async-compatible session wrappers.
- Entry-point registration under `tigrbl.engine` with `kind="membloom"`.

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
    if db.add_if_absent(key):
        return {"status": "accepted"}
    return {"status": "duplicate"}
```

The session object exposes `add`, `contains`, `add_if_absent`, `reset`, and `stats`.

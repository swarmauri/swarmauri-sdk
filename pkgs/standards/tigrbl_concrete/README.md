![Tigrbl branding](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

# tigrbl-concrete

![PyPI - Downloads](https://img.shields.io/pypi/dm/tigrbl-concrete.svg) ![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg) ![Python Versions](https://img.shields.io/pypi/pyversions/tigrbl-concrete.svg) ![License](https://img.shields.io/pypi/l/tigrbl-concrete.svg) ![Version](https://img.shields.io/pypi/v/tigrbl-concrete.svg)

## Features

- Modular package in the Tigrbl namespace.
- Supports Python 3.10 through 3.12.
- Distributed as part of the swarmauri-sdk workspace.

## Installation

### uv

```bash
uv add tigrbl-concrete
```

### pip

```bash
pip install tigrbl-concrete
```

## Usage

Import from the shared package-specific module namespaces after installation in your environment.

### Runtime-visible operation metadata

Runtime-visible operations are defined by collected specs (`RouterSpec.collect(...)`,
`OpSpec.collect(...)`) and then installed through binding on the live graph.
Mounted routes are not backfilled into runtime metadata after the fact.

```python
from tigrbl_concrete import TigrblApp, TigrblRouter

app = TigrblApp()
router = TigrblRouter()

@router.get("/health")
def health_check():
    return {"ok": True}

# include_router(...) mounts already-bound operations
app.include_router(router, prefix="/api")
```

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

### Runtime route metadata registration with `TigrblApp`

`TigrblApp` automatically reflects imperative routes into Tigrbl operation metadata.
This means `add_route(...)` and `include_router(...)` both call the concrete
runtime route binder (`tigrbl_concrete._concrete.runtime_route_binding.register_runtime_route`) for mounted routes.

```python
from tigrbl_concrete import TigrblApp, TigrblRouter

app = TigrblApp()
router = TigrblRouter()

@router.get("/health")
def health_check():
    return {"ok": True}

# include_router(...) mounts router routes and mirrors them into op metadata
app.include_router(router, prefix="/api")

# add_route(...) also mirrors the single imperative route into op metadata
app.add_route("/ping", lambda request: {"ping": "pong"}, methods=["GET"])
```

### Direct binder usage (advanced)

If you are integrating custom route mounting internals, you can invoke the binder directly:

```python
from tigrbl_concrete._concrete.runtime_route_binding import register_runtime_route

# app: TigrblApp-like object
# route: mounted route object
register_runtime_route(app, route)
```

![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl-concrete/">
        <img src="https://static.pepy.tech/badge/tigrbl-concrete/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_concrete/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_concrete.svg"/></a>
    <a href="https://pypi.org/project/tigrbl-concrete/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl-concrete" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl-concrete/">
        <img src="https://img.shields.io/pypi/l/tigrbl-concrete" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl-concrete/">
        <img src="https://img.shields.io/pypi/v/tigrbl-concrete?label=tigrbl-concrete&color=green" alt="PyPI - tigrbl-concrete"/></a>
</p>
---

# tigrbl-concrete

![PyPI - Downloads](https://static.pepy.tech/badge/tigrbl-concrete/month) ![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg) ![Python Versions](https://img.shields.io/pypi/pyversions/tigrbl-concrete.svg) ![License](https://img.shields.io/pypi/l/tigrbl-concrete.svg) ![Version](https://img.shields.io/pypi/v/tigrbl-concrete.svg)

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

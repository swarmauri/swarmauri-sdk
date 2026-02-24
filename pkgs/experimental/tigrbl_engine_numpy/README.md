![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pypi.org/project/tigrbl_engine_numpy/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_numpy?label=tigrbl_engine_numpy&color=green" alt="PyPI - tigrbl_engine_numpy"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_engine_numpy/">
        <img src="https://img.shields.io/pypi/dm/tigrbl_engine_numpy" alt="PyPI - Downloads"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_engine_numpy/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_engine_numpy" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_engine_numpy/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_numpy" alt="PyPI - License"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_numpy/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_numpy.svg"/>
    </a>
</p>

# tigrbl_engine_numpy

A tigrbl engine plugin that registers `kind="numpy"` where each array/matrix is a single-table database-like object.

## Features

- Registers a `numpy` engine through the `tigrbl.engine` entry-point group.
- Treats one NumPy array/matrix as one table.
- Provides a first-class `NumpySession` (subclass of `TigrblSessionBase`) without pandas dependencies.
- Supports loading `.npy`/`.npz` via `np.load(...)`, memory-mapped arrays via `np.memmap(...)`, and persistence via `np.save(...)`.

## Installation

### uv

```bash
uv add tigrbl_engine_numpy
```

### pip

```bash
pip install tigrbl_engine_numpy
```

## Usage

```python
import numpy as np
from tigrbl.engine import EngineSpec

spec = EngineSpec(kind="numpy", mapping={"array": np.array([[1, 2], [3, 4]]), "columns": ["id", "value"], "table": "matrix", "pk": "id"})
provider = spec.provider()
engine, session_factory = provider.build()

session = session_factory()
print(session.array())
print(session.to_records())
session.close()
```

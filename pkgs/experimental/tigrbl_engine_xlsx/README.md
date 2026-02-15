![Tigrbl Logo](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/tigrbl_engine_xlsx/">
        <img src="https://img.shields.io/pypi/v/tigrbl_engine_xlsx?label=tigrbl_engine_xlsx&color=green" alt="PyPI - tigrbl_engine_xlsx"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_engine_xlsx/">
        <img src="https://img.shields.io/pypi/dm/tigrbl_engine_xlsx" alt="PyPI - Downloads"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_engine_xlsx/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_engine_xlsx" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_engine_xlsx/">
        <img src="https://img.shields.io/pypi/l/tigrbl_engine_xlsx" alt="PyPI - License"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_xlsx/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/tigrbl_engine_xlsx.svg"/>
    </a>
</p>

# tigrbl_engine_xlsx

A tigrbl engine plugin where each workbook is a database-like object and each sheet is a table.

## Features

- Registers `kind="xlsx"` through the `tigrbl.engine` entry-point group.
- Uses `load_workbook`, `wb[...]`, and `wb.save(...)` directly for workbook operations.
- Treats each sheet as a table with transactional table semantics.

## Installation

### uv

```bash
uv add tigrbl_engine_xlsx
```

### pip

```bash
pip install tigrbl_engine_xlsx
```

## Usage

```python
from tigrbl.engine import EngineSpec

spec = EngineSpec(kind="xlsx", mapping={"path": "./workbook.xlsx", "pk": "id"})
provider = spec.provider()
engine, session_factory = provider.build()

session = session_factory()
wb = session.workbook()
print(wb["Sheet1"])
print(session.table("Sheet1"))
```

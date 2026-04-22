![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/mto/">
        <img src="https://img.shields.io/pypi/v/mto?label=mto&color=green" alt="PyPI - mto"/>
    </a>
    <a href="https://pepy.tech/project/mto/">
        <img src="https://static.pepy.tech/badge/mto/month" alt="PyPI - Downloads"/>
    </a>
    <a href="https://pypi.org/project/mto/">
        <img src="https://img.shields.io/pypi/pyversions/mto" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/mto/">
        <img src="https://img.shields.io/pypi/l/mto" alt="PyPI - License"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/mto/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/mto.svg"/>
    </a>
</p>

# mto

`mto` is a planning-stage placeholder reservation for monotone operators.

The package reserves the short `mto` distribution and import coordinate while the operator
catalog is governed and finalized. The intended scope is a compact monotone-operator toolkit
for deterministic aggregation, lattice and semilattice joins, CRDT-style state merges,
fixpoint workflows, evidence rollups, and related positive dataflow patterns.

`mto` supports Python 3.10 through 3.12.

## Features

- Reserves the `mto` package coordinate for monotone-operator work.
- Documents the intended monotone-operator scope without exposing provisional APIs.
- Provides a typed import package with placeholder metadata for downstream planning checks.

## Installation

### uv

```bash
uv add mto
```

### pip

```bash
pip install mto
```

## Usage

The package module is `mto`.

```python
import mto

assert mto.__version__ == "0.1.0"
assert mto.PLANNING_STAGE is True
```

No monotone-operator APIs are committed yet. Future APIs should be added only after the
operator catalog, naming, and compatibility surface are finalized.

## Development

```bash
uv run --directory pkgs --package mto ruff format experimental/mto
uv run --directory pkgs --package mto ruff check experimental/mto --fix
uv run --directory pkgs --package mto pytest experimental/mto/tests
```

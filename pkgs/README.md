![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_monorepo/">
        <img src="https://static.pepy.tech/badge/swarmauri_monorepo/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_monorepo/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_monorepo" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_monorepo/">
        <img src="https://img.shields.io/pypi/l/swarmauri_monorepo" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_monorepo/">
        <img src="https://img.shields.io/pypi/v/swarmauri_monorepo?label=swarmauri_monorepo&color=green" alt="PyPI - swarmauri_monorepo"/></a>
</p>
---

`swarmauri_monorepo` is the workspace package that groups the Swarmauri SDK's interdependent Python packages under a single `uv` workspace for local development, validation, and coordinated release management.

## Features

- Centralizes the `pkgs/` workspace manifest for the Swarmauri SDK package fleet.
- Provides one install surface for local workspace development across standards, community, experimental, and plugin packages.
- Keeps shared dependency and tooling constraints aligned for Python 3.10 through 3.12.

## Installation

### `uv`

```bash
uv sync --directory pkgs
```

### `pip`

```bash
pip install swarmauri_monorepo
```

## Usage

Use the workspace package when you need to install or validate the entire `pkgs/` tree as one coordinated environment.

```bash
uv run --directory pkgs pytest
```

```bash
uv run --directory pkgs ruff check .
```

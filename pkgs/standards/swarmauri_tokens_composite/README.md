![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_composite" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_composite/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_composite.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_composite" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_composite" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_composite/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_composite?label=swarmauri_tokens_composite&color=green" alt="PyPI - swarmauri_tokens_composite"/></a>
</p>

---

## Swarmauri Token Composite

Algorithm-routing token service delegating to child providers based on JWT headers, claims, or algorithms.

## Installation

```bash
pip install swarmauri_tokens_composite
```

## Usage

```python
from swarmauri_tokens_composite import CompositeTokenService

svc = CompositeTokenService([...])  # pass in other ITokenService providers
```

## Entry point

The provider is registered under the `swarmauri.tokens` entry-point as `CompositeTokenService`.

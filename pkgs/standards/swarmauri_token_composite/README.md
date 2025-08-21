![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_token_composite/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_token_composite" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_token_composite/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_token_composite.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_token_composite/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_token_composite" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_token_composite/">
        <img src="https://img.shields.io/pypi/l/swarmauri_token_composite" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_token_composite/">
        <img src="https://img.shields.io/pypi/v/swarmauri_token_composite?label=swarmauri_token_composite&color=green" alt="PyPI - swarmauri_token_composite"/></a>
</p>

---

## Swarmauri Token Composite

Algorithm-routing token service delegating to child providers based on JWT headers, claims, or algorithms.

## Installation

```bash
pip install swarmauri_token_composite
```

## Usage

```python
from swarmauri_token_composite import CompositeTokenService

svc = CompositeTokenService([...])  # pass in other ITokenService providers
```

## Entry point

The provider is registered under the `swarmauri.tokens` entry-point as `CompositeTokenService`.

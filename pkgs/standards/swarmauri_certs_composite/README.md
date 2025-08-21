![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_certs_composite/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_certs_composite" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_composite/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_certs_composite.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_composite/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_certs_composite" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_composite/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_composite" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_composite/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_composite?label=swarmauri_certs_composite&color=green" alt="PyPI - swarmauri_certs_composite"/></a>
</p>

---

## Swarmauri Certs Composite

Routing certificate service delegating to child providers based on requested features.

## Installation

```bash
pip install swarmauri_certs_composite
```

## Usage

```python
from swarmauri_certs_composite import CompositeCertService

svc = CompositeCertService([...])  # pass in other ICertService providers
```

## Entry point

The provider is registered under the `swarmauri.certs` entry-point as `CompositeCertService`.

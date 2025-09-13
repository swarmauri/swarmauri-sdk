![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-token-introspection/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-token-introspection" alt="PyPI - Downloads"/>
    </a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri-token-introspection">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri-token-introspection&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-token-introspection/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-token-introspection" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-token-introspection/">
        <img src="https://img.shields.io/pypi/l/swarmauri-token-introspection" alt="PyPI - License"/>
    </a>
    <br />
    <a href="https://pypi.org/project/swarmauri-token-introspection/">
        <img src="https://img.shields.io/pypi/v/swarmauri-token-introspection?label=swarmauri-token-introspection&color=green" alt="PyPI - swarmauri-token-introspection"/>
    </a>
</p>

---

# `swarmauri-token-introspection`

An OAuth 2.0 token introspection service plugin implementing RFC 7662 for verifying opaque access tokens.

## Purpose

This package provides an asynchronous token service that validates opaque tokens against a remote introspection endpoint and enforces standard claim checks.

## Installation

To install `swarmauri-token-introspection`, you can use Poetry or pip:

```bash
pip install swarmauri-token-introspection
```

## Usage

```python
from swarmauri_tokens_introspection import IntrospectionTokenService

service = IntrospectionTokenService("https://auth.example.com/introspect", client_id="id", client_secret="secret")
claims = await service.verify("opaque-token")
```

## License

`Apache-2.0` © Swarmauri


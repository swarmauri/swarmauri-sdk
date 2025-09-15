![Tigrbl Logo](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/tigrbl_client/">
        <img src="https://img.shields.io/pypi/v/tigrbl_client?label=tigrbl_client&color=green" alt="PyPI - tigrbl_client"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_client/">
        <img src="https://img.shields.io/pypi/dm/tigrbl_client" alt="PyPI - Downloads"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_client/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_client" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/tigrbl_client/">
        <img src="https://img.shields.io/pypi/l/tigrbl_client" alt="PyPI - License"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_client/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_client.svg"/>
    </a>
</p>

---

# Tigrbl Client 🐅

A lightweight HTTP client for interacting with Tigrbl services.
Tigrbl exposes operations under resource-based namespaces such as
`api.core.Users.create` or `api.rpc.Users.login`, all accessible via
this client.

## Features ✨

- Minimal dependencies with friendly typing
- Automatic JSON serialization / deserialization
- Simple namespace-based method access

## Installation 📦

```bash
pip install tigrbl_client
```

## Quick Start 🚀

```python
from tigrbl_client import Client

client = Client("https://api.tigrbl.io", token="your-token")
response = client.api.core.Users.read(id=1)
print(response)
```

## License 📝

This project is licensed under the terms of the [MIT license](LICENSE).

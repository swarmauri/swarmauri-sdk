![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_auth_idp_okta/">
        <img src="https://static.pepy.tech/badge/swarmauri_auth_idp_okta/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_auth_idp_okta/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_auth_idp_okta.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_okta/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_okta/">
        <img src="https://img.shields.io/pypi/l/swarmauri_auth_idp_okta" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_auth_idp_okta/">
        <img src="https://img.shields.io/pypi/v/swarmauri_auth_idp_okta?label=swarmauri_auth_idp_okta&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Auth IDP Okta

Okta OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri.

## Features

- Okta OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri.
- Exposes discoverable runtime entry points for `swarmauri.auth_idp` so the package can be wired into Swarmauri or Tigrbl workflows.
- Fits the standards package lane so the capability can be added to a project as a focused, separately versioned dependency.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_auth_idp_okta
```

```bash
pip install swarmauri_auth_idp_okta
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_auth_idp_okta import OktaOAuth20AppClient, OktaOAuth20Login, OktaOAuth21AppClient, OktaOAuth21Login

exports = ['OktaOAuth20AppClient', 'OktaOAuth20Login', 'OktaOAuth21AppClient', 'OktaOAuth21Login']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.

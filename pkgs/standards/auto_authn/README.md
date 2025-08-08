![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/auto_authn/">
        <img src="https://img.shields.io/pypi/dm/auto_authn" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/auto_authn/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/auto_authn.svg"/></a>
    <a href="https://pypi.org/project/auto_authn/">
        <img src="https://img.shields.io/pypi/pyversions/auto_authn" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/auto_authn/">
        <img src="https://img.shields.io/pypi/l/auto_authn" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/auto_authn/">
        <img src="https://img.shields.io/pypi/v/auto_authn?label=auto_authn&color=green" alt="PyPI - auto_authn"/></a>
</p>

---

# Auto Authn: Multi-Tenant OpenID Connect Provider

`Auto Authn` is an async, SQL-backed Identity Provider for OpenID Connect 1.0 and OAuth 2.1.
It provides per-tenant isolation and is designed to scale for SaaS deployments.

## Features

- Per-tenant issuer URLs with isolated user and client tables.
- RSA-based JWT signing with helpers for key rotation.
- FastAPI and SQLAlchemy 2.0 async stack.

## Installation

```bash
pip install auto_authn
```

## Quick Start

```python
from auto_authn.app import create_app

app = create_app()
```

Check the documentation for detailed setup and configuration.


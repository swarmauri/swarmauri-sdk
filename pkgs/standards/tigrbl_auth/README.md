![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/tigrbl_auth/">
        <img src="https://img.shields.io/pypi/dm/tigrbl_auth" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_auth/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_auth.svg"/></a>
    <a href="https://pypi.org/project/tigrbl_auth/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl_auth" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl_auth/">
        <img src="https://img.shields.io/pypi/l/tigrbl_auth" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl_auth/">
        <img src="https://img.shields.io/pypi/v/tigrbl_auth?label=tigrbl_auth&color=green" alt="PyPI - tigrbl_auth"/></a>
</p>

### Terminology

- **Tenant** – a namespace used to group related resources such as repositories or clients.
- **Principal** – an owner of resources, for example an individual user or an organization.

---

# Auto Authn: Multi-Tenant OpenID Connect Provider

`Auto Authn` is an async, SQL-backed Identity Provider for OpenID Connect 1.0 and OAuth 2.1.
It provides per-tenant isolation and is designed to scale for SaaS deployments.

## Features

- Per-tenant issuer URLs with isolated user and client tables.
- RSA-based JWT signing with helpers for key rotation.
- FastAPI and SQLAlchemy 2.0 async stack.
- OIDC discovery endpoints and JWKS generation.
- Configurable PostgreSQL or SQLite storage with optional Redis support.

## Installation

```bash
pip install tigrbl_auth
```

Extras are available for common database drivers:

```bash
# PostgreSQL
pip install tigrbl_auth[postgres]

# SQLite
pip install tigrbl_auth[sqlite]
```

## Quick Start

```python
from tigrbl_auth.app import create_app

app = create_app()
```

The embedded ``surface_api`` exposes resource and flow operations for in-process usage via
namespaces like ``surface_api.core.User.create``.

Check the documentation for detailed setup and configuration.

To run the API locally with Uvicorn:

```bash
uvicorn tigrbl_auth.app:app --reload
```

The service exposes an OpenID Connect discovery document at
`/.well-known/openid-configuration` and publishes its JSON Web Key Set at
`/.well-known/jwks.json`.

## Configuration

`Auto Authn` reads settings from environment variables. Common options include:

- `PG_DSN` or the combination of `PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, `PG_PASS`
  for database connectivity.
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, and `REDIS_PASSWORD` for Redis session
  storage (optional).
- `JWT_SECRET` for token signing and `LOG_LEVEL` to control logging verbosity.

## Docker

A lightweight Dockerfile is provided. Build and run the service with:

```bash
docker build -t tigrbl-auth .
docker run -p 8000:8000 tigrbl-auth
```

Visit `http://localhost:8000/docs` to explore the interactive API documentation.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request to
discuss improvements.

## License

Apache-2.0


![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_introspection/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_introspection" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_introspection/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_introspection.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_tokens_introspection/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_introspection" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_tokens_introspection/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_introspection" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_tokens_introspection/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_introspection?label=swarmauri_tokens_introspection&color=green" alt="PyPI - swarmauri_tokens_introspection"/>
    </a>
</p>

---

# swarmauri_tokens_introspection

An OAuth 2.0 token introspection service plugin implementing RFC 7662 for verifying opaque access tokens.

## Features

- Asynchronous token verification against a remote introspection endpoint
- Supports `client_secret_basic`, `client_secret_post`, and bearer authentication
- Caches positive and negative introspection results with configurable TTLs
- Validates standard claims (`exp`, `nbf`, `iat`) with optional issuer and audience checks
- Optional JWKS passthrough for issuers that also publish signing keys

## Installation

```bash
pip install swarmauri_tokens_introspection
```

## Usage

```python
from swarmauri_tokens_introspection import IntrospectionTokenService

service = IntrospectionTokenService(
    "https://auth.example.com/introspect",
    client_id="id",
    client_secret="secret",
)
claims = await service.verify("opaque-token")
```

## License

`Apache-2.0` © Swarmauri


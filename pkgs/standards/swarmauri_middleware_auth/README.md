![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_auth/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_auth" alt="PyPI - Downloads"/>
    </a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri_middleware_auth">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri_middleware_auth&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_auth/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_auth" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_auth/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_auth" alt="PyPI - License"/>
    </a>
    <br />
    <a href="https://pypi.org/project/swarmauri_middleware_auth/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_auth?label=swarmauri_middleware_auth&color=green" alt="PyPI - swarmauri_middleware_auth"/>
    </a>
</p>

---

# `swarmauri_middleware_auth`

JWT authentication middleware for Swarmauri and FastAPI applications.

## Features

- Validates `Bearer` tokens in incoming requests
- Verifies signatures using `swarmauri_signing_jws`
- Supports expiration, audience and issuer checks
- Provides hooks for custom claim validation
- Offers a utility to verify tokens outside the middleware

## Installation

```bash
pip install swarmauri_middleware_auth
# or
poetry add swarmauri_middleware_auth
```

## Usage

```python
from fastapi import FastAPI
from swarmauri_middleware_auth import AuthMiddleware

app = FastAPI()
app.add_middleware(
    AuthMiddleware,
    secret_key="supersecret",
    issuer="my-service",
    audience="my-audience",
)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).


![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-middleware-securityheaders/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-middleware-securityheaders" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_securityheaders/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_securityheaders.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-middleware-securityheaders/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-middleware-securityheaders" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-middleware-securityheaders/">
        <img src="https://img.shields.io/pypi/l/swarmauri-middleware-securityheaders" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri-middleware-securityheaders/">
        <img src="https://img.shields.io/pypi/v/swarmauri-middleware-securityheaders?label=swarmauri-middleware-securityheaders&color=green" alt="PyPI - swarmauri-middleware-securityheaders"/>
    </a>
</p>

---

# Swarmauri Middleware Security Headers

Middleware for adding security-focused HTTP headers to FastAPI responses, helping shield applications from common web vulnerabilities.

## Installation

```bash
pip install swarmauri-middleware-securityheaders
```

## Usage

```python
from fastapi import FastAPI
from swarmauri_middleware_securityheaders import SecurityHeadersMiddleware

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.

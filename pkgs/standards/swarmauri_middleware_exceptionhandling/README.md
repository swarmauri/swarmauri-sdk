![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_exceptionhandling/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_exceptionhandling" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_exceptionhandling/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_exceptionhandling.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_exceptionhandling/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_exceptionhandling" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_exceptionhandling/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_exceptionhandling" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_exceptionhandling/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_exceptionhandling?label=swarmauri_middleware_exceptionhandling&color=green" alt="PyPI - swarmauri_middleware_exceptionhandling"/>
    </a>
</p>

---

# Swarmauri Middleware Exception Handling

Centralized exception and error handling for Swarmauri applications built on FastAPI.

## Installation

```bash
pip install swarmauri_middleware_exceptionhandling
```

## Usage

```python
from fastapi import FastAPI
from swarmauri_middleware_exceptionhandling import ExceptionHandlingMiddleware

app = FastAPI()
app.middleware("http")(ExceptionHandlingMiddleware())
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_llamaguard/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_llamaguard" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_llamaguard/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_llamaguard.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_llamaguard/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_llamaguard" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_llamaguard/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_llamaguard" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_llamaguard/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_llamaguard?label=swarmauri_middleware_llamaguard&color=green" alt="PyPI - swarmauri_middleware_llamaguard"/>
    </a>
</p>

---

# Swarmauri Middleware LlamaGuard

A FastAPI middleware that integrates LlamaGuard for comprehensive content inspection and filtering, ensuring requests and responses are free from unsafe or malicious content.

## Features

- Real-time scanning of incoming and outgoing payloads.
- Configurable safety policies and thresholds.
- Seamless drop-in middleware for any FastAPI application.

## Installation

```bash
pip install swarmauri_middleware_llamaguard
```

## Usage

```python
from fastapi import FastAPI
from swarmauri_middleware_llamaguard import LlamaGuardMiddleware

app = FastAPI()

# Add LlamaGuard with default settings
app.add_middleware(LlamaGuardMiddleware)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

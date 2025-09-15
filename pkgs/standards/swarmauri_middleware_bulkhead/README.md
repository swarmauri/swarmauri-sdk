![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_bulkhead/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_bulkhead" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_bulkhead/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_bulkhead.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_bulkhead/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_bulkhead" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_bulkhead/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_bulkhead" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_bulkhead/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_bulkhead?label=swarmauri_middleware_bulkhead&color=green" alt="PyPI - swarmauri_middleware_bulkhead"/>
    </a>
</p>

---

# Swarmauri Middleware Bulkhead

Concurrency isolation middleware for FastAPI applications. Limit the number of simultaneous requests to protect resources from overload and ensure reliable service operation.

## Features

- **Concurrency control** to restrict the maximum number of in-flight requests
- **Semaphore-based management** for efficient request queuing and processing
- **Logging integration** to provide visibility into request flow and errors
- **Configurable limits** to match your service capacity
- **FastAPI compatibility** for seamless integration

## Installation

```bash
pip install swarmauri_middleware_bulkhead
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md).


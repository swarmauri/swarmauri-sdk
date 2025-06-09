![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_jsonrpc/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_jsonrpc" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_jsonrpc/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_jsonrpc.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_jsonrpc/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_jsonrpc" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_jsonrpc/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_jsonrpc" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_jsonrpc/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_jsonrpc?label=swarmauri_middleware_jsonrpc&color=green" alt="PyPI - swarmauri_middleware_jsonrpc"/>
    </a>
</p>

---

# Swarmauri Middleware JsonRpc

Middleware that performs simple validation of JSON-RPC requests.

## Usage

```python
from fastapi import FastAPI
from swarmauri_middleware_jsonrpc import JsonRpcMiddleware

app = FastAPI()
app.middleware("http")(JsonRpcMiddleware().dispatch)
```

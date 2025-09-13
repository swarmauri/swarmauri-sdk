![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

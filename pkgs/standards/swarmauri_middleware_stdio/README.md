![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_stdio/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_stdio" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_stdio/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_stdio.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_stdio/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_stdio" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_stdio/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_stdio" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_stdio/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_stdio?label=swarmauri_middleware_stdio&color=green" alt="PyPI - swarmauri_middleware_stdio"/>
    </a>
</p>

---

# Swarmauri Middleware Stdio

Middleware that logs requests and responses to standard output.

## Usage

```python
from fastapi import FastAPI
from swarmauri_middleware_stdio import StdioMiddleware

app = FastAPI()
app.middleware("http")(StdioMiddleware().dispatch)

@app.get("/")
async def hello() -> dict[str, str]:
    return {"message": "hello"}
```

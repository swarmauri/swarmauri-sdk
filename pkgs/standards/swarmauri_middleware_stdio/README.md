<!-- Dark OS/GitHub theme → show LIGHT PNG; Light → show DARK PNG -->
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="../../../assets/swarmauri_brand_frag_light.png">
  <source media="(prefers-color-scheme: light)" srcset="../../../assets/swarmauri_brand_frag_dark.png">
  <!-- Fallback below (see #2) -->
  <img alt="Project logo" src="../../../assets/swarmauri_brand_frag_dark.png" width="640">
</picture>


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

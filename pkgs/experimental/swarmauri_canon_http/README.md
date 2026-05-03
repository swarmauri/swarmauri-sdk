![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri-canon-http/">
        <img src="https://static.pepy.tech/badge/swarmauri-canon-http/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_canon_http/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_canon_http.svg"/></a>
    <a href="https://pypi.org/project/swarmauri-canon-http/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-canon-http" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri-canon-http/">
        <img src="https://img.shields.io/pypi/l/swarmauri-canon-http" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri-canon-http/">
        <img src="https://img.shields.io/pypi/v/swarmauri-canon-http?label=swarmauri-canon-http&color=green" alt="PyPI - swarmauri-canon-http"/></a>
</p>

---

`swarmauri_canon_http` is a lightweight canonical HTTP client implementation that tracks a subset of `httpx` behavior for parity checks and incremental feature alignment.

## Features

- Sync request helpers: `get`, `post`, `put`, `patch`, `delete`, `head`, `options`
- Async request helpers: `aget`, `apost`, `aput`, `apatch`, `adelete`, `ahead`, `aoptions`
- Query parameter support (`params`)
- Header support (`headers`)
- JSON body serialization (`json_data`)
- HTTP/1.1 support
- Experimental HTTP/2 pathway

### HTTPX surface parity map

The parity tests are organized into `tests/parity/httpx/` and `tests/parity/requests/`, and use shared parity helpers to document supported and currently-missing surface area.

| Feature area | httpx | swarmauri_canon_http |
| --- | --- | --- |
| Auth (`auth=`) | âœ… | âŒ (not implemented) |
| Cookies (`cookies=`) | âœ… | âŒ (not implemented) |
| Rich Request/Response model | âœ… | âŒ (primitive tuple/string responses) |
| `request(...)` generic API | âœ… | âš ï¸ (`sync_request`/`async_request` only) |
| Streaming API (`stream`) | âœ… | âŒ |
| HTTP/1 + HTTP/2 toggles | âœ… | âš ï¸ (`version="1.1"` or `"2"`) |
| HTTP/3 | âŒ | âŒ |
| WebSocket schemes (`ws://`, `wss://`) | âŒ | âŒ |
| SSL verify/cert keyword options | âœ… | âŒ (constructor does not accept `verify`/`cert`) |
| Async client support | âœ… | âœ… |

## Installation

### With `uv`

```bash
uv add swarmauri-canon-http
```

### With `pip`

```bash
pip install swarmauri-canon-http
```

## Usage

### Sync workflow

```python
from swarmauri_canon_http import HttpClient

client = HttpClient(base_url="https://example.com", timeout=5)
status, headers, body = client.get("/health", params={"full": "1"})
print(status, body)
```

### Async workflow

```python
import asyncio
from swarmauri_canon_http import HttpClient


async def main():
    client = HttpClient(base_url="https://example.com", timeout=5)
    raw_response = await client.aget("/health")
    print(raw_response)


asyncio.run(main())
```

## Python support

This package targets Python 3.10 through 3.12 in project-level documentation.

![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_ratelimit/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_ratelimit" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_ratelimit/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_ratelimit.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratelimit/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_ratelimit" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratelimit/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_ratelimit" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratelimit/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_ratelimit?label=swarmauri_middleware_ratelimit&color=green" alt="PyPI - swarmauri_middleware_ratelimit"/>
    </a>
</p>

---

# Swarmauri Middleware Ratelimit

Flexible rate limiting middleware for Swarmauri applications.

This package provides a drop-in FastAPI middleware that throttles requests
based on the client IP address or an authentication token. It is useful for
preventing abuse of public APIs or protecting upstream services from bursts of
traffic.

## Features

- Configurable request limit and time window.
- Supports IP-based or token-based identification.
- Returns `429` responses when the limit is exceeded.

## Installation

```bash
pip install swarmauri_middleware_ratelimit
```

## Usage

```python
from fastapi import FastAPI
from swarmauri_middleware_ratelimit import RateLimitMiddleware

app = FastAPI()

# Allow 100 requests per minute per client IP
app.add_middleware(RateLimitMiddleware, rate_limit=100, time_window=60)
```

### Token-based rate limiting

```python
# Use the value of the `X-Api-Key` header to track clients
app.add_middleware(
    RateLimitMiddleware,
    rate_limit=100,
    time_window=60,
    use_token=True,
    token_header="X-Api-Key",
)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

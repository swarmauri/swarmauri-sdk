![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_middleware_securityheaders/">
        <img src="https://static.pepy.tech/badge/swarmauri_middleware_securityheaders/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_securityheaders/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_securityheaders.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_securityheaders/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_securityheaders/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_securityheaders" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_securityheaders/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_securityheaders?label=swarmauri_middleware_securityheaders&color=green" alt="PyPI - swarmauri_middleware_securityheaders"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Middleware Security Headers

Middleware for adding security-focused HTTP headers to FastAPI responses, helping shield applications from common web vulnerabilities.

## What it does

`SecurityHeadersMiddleware` ensures every response produced by your FastAPI
application carries the following headers and values:

- `Content-Security-Policy`: `default-src 'self'; script-src 'self'
  https://cdn.example.com; style-src 'self' https://cdn.example.com; img-src
  'self' https://images.example.com; font-src 'self'
  https://fonts.example.com`
- `X-Content-Type-Options`: `nosniff`
- `X-Frame-Options`: `DENY`
- `X-XSS-Protection`: `1; mode=block`
- `Strict-Transport-Security`: `max-age=31536000; includeSubDomains; preload`
- `Referrer-Policy`: `same-origin`
- `Permissions-Policy`: `interest-cohort=(), geolocation=(self),
  microphone=(), camera=(), magnetometer=(), gyroscope=(), speaker=(self),
  vibrate=(), payment=()`

These defaults provide a strong baseline for many applications. Update the
middleware if you need to tailor the directives (for example, to change the
allowed host names in the Content Security Policy).

## Installation

### pip

```bash
pip install swarmauri-middleware-securityheaders
```

### Poetry

```bash
poetry add swarmauri_middleware_securityheaders
```

### uv

```bash
uv add swarmauri_middleware_securityheaders
```

## Usage

```python
from fastapi import FastAPI, Request
from swarmauri_middleware_securityheaders import SecurityHeadersMiddleware

app = FastAPI()
security_middleware = SecurityHeadersMiddleware(app)


@app.middleware("http")
async def apply_security_headers(request: Request, call_next):
    return await security_middleware.dispatch(request, call_next)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"status": "ok"}
```

This pattern instantiates the middleware once and reuses its `dispatch` method
within FastAPI's `@app.middleware("http")` hook so that every response includes
the security headers listed above.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.



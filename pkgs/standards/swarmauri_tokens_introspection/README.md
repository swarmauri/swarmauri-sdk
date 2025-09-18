![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_introspection/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_introspection" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_introspection/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_introspection.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_tokens_introspection/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_introspection" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_tokens_introspection/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_introspection" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_tokens_introspection/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_introspection?label=swarmauri_tokens_introspection&color=green" alt="PyPI - swarmauri_tokens_introspection"/>
    </a>
</p>

---

# swarmauri_tokens_introspection

An OAuth 2.0 token introspection service plugin implementing RFC 7662 for verifying opaque access tokens.

## Features

- Asynchronous token verification against a remote introspection endpoint using `httpx`
- Supports `client_secret_basic`, `client_secret_post`, and bearer authentication schemes
- Caches positive and negative introspection results with configurable TTLs and expiry-aware caching
- Validates standard claims (`exp`, `nbf`, `iat`) with optional issuer and audience enforcement
- Optional JWKS passthrough for issuers that also publish signing keys via `jwks_url`
- Strictly verification-only: `mint()` raises `NotImplementedError` because opaque tokens are produced by the authorization server

## Installation

Choose the toolchain that matches your project:

```bash
pip install swarmauri_tokens_introspection
```

```bash
poetry add swarmauri_tokens_introspection
```

```bash
uv add swarmauri_tokens_introspection
```

The package exposes an async API, so ensure your environment includes an event loop (e.g., `asyncio`) when calling it.

## Usage

The example below demonstrates how to exercise the service with a mocked introspection endpoint. The same API works against a live OAuth 2.0 Authorization Server—simply omit the mock transport and let `httpx` reach your configured `endpoint`.

```python
"""Execute the README example with `python README_example.py`."""

import asyncio

import httpx

from swarmauri_tokens_introspection import IntrospectionTokenService


async def main() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url == httpx.URL("https://auth.example.com/introspect")
        assert request.headers["Authorization"].startswith("Basic ")
        form = dict(httpx.QueryParams(request.content.decode()))
        assert form["token"] == "opaque-token"
        return httpx.Response(
            200,
            json={
                "active": True,
                "sub": "user-123",
                "scope": "profile email",
                "exp": 2_147_483_647,
            },
        )

    transport = httpx.MockTransport(handler)

    service = IntrospectionTokenService(
        "https://auth.example.com/introspect",
        client_id="id",
        client_secret="secret",
        cache_ttl_s=300,
    )

    # Inject the mock transport; in production you would not override the client.
    service._client = httpx.AsyncClient(transport=transport)

    claims = await service.verify("opaque-token")
    print(claims["sub"])  # user-123

    await service.aclose()


if __name__ == "__main__":
    asyncio.run(main())
```

### Caching and validation highlights

- Positive responses respect both `cache_ttl_s` and the `exp` claim (including the configured leeway).
- Negative introspection results are cached for `negative_ttl_s` seconds to shield your AS from repeated invalid requests.
- Local validation enforces `exp`, `nbf`, and `iat` drift using `leeway_s`, and supports issuer/audience pinning.
- Configuring `jwks_url` enables `jwks()` passthrough for deployments that expose signing keys alongside introspection.

## License

`Apache-2.0` © Swarmauri

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_remoteoidc/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_remoteoidc" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_remoteoidc/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_remoteoidc.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_remoteoidc/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_remoteoidc" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_remoteoidc/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_remoteoidc" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_remoteoidc/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_remoteoidc?label=swarmauri_tokens_remoteoidc&color=green" alt="PyPI - swarmauri_tokens_remoteoidc"/></a>

</p>

---

# swarmauri_tokens_remoteoidc

Remote OIDC token verification service for Swarmauri.

This package provides a verification-only token service that retrieves
JSON Web Key Sets (JWKS) from a remote OpenID Connect (OIDC) issuer and
validates JWTs in accordance with RFC 7517 and RFC 7519. It implements
`ITokenService` and exposes an entry point named
`RemoteOIDCTokenService`.

## Features

- Remote OIDC discovery with JWKS caching and conditional revalidation
  (ETag / Last-Modified).
- Audience and issuer validation with configurable clock-skew leeway.
- Optional extras for additional canonicalisation formats via the `cbor`
  extra.
- Manual refresh hook for cache priming plus a `jwks()` helper for
  introspection.
- Verification-only surface: `mint()` deliberately raises
  `NotImplementedError`.

## Installation

### pip

```bash
pip install swarmauri_tokens_remoteoidc
```

### Poetry

```bash
poetry add swarmauri_tokens_remoteoidc
```

### uv

```bash
uv add swarmauri_tokens_remoteoidc
```

Install the optional CBOR canonicalisation helpers with the `cbor`
extra if needed:

```bash
pip install swarmauri_tokens_remoteoidc[cbor]
poetry add --extras cbor swarmauri_tokens_remoteoidc
uv add swarmauri_tokens_remoteoidc[cbor]
```

## Usage

1. Provide the expected OIDC issuer URL. Optionally override
   `jwks_url` to skip discovery when you already know the JWKS endpoint.
2. Call `refresh()` to prime caches when your process boots or after a
   rotation signal.
3. Await `verify()` with the JWT to validate signatures, issuer, and
   optional audience or nonce constraints.

### Example

The snippet below boots a minimal HTTP server that hosts a JWKS
containing a symmetric key. It then mints a short-lived HS256 token and
verifies it using `RemoteOIDCTokenService`.

```python
import asyncio
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import jwt
from jwt.utils import base64url_encode

from swarmauri_tokens_remoteoidc import RemoteOIDCTokenService

SECRET = b"super-secret-key"
KEY_ID = "demo-key"


def make_handler(jwks: dict):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/jwks.json":
                self.send_response(404)
                self.end_headers()
                return

            body = json.dumps(jwks).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):  # pragma: no cover - quiet server
            return

    return Handler


async def main() -> None:
    jwks = {
        "keys": [
            {
                "kty": "oct",
                "kid": KEY_ID,
                "k": base64url_encode(SECRET).decode("ascii"),
                "alg": "HS256",
            }
        ]
    }

    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(jwks))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        issuer = "https://issuer.example.com"
        jwks_url = f"http://127.0.0.1:{server.server_address[1]}/jwks.json"

        service = RemoteOIDCTokenService(
            issuer=issuer,
            jwks_url=jwks_url,
            expected_alg_whitelist=("HS256",),
        )

        now = int(time.time())
        token = jwt.encode(
            {
                "iss": issuer,
                "aud": "my-audience",
                "sub": "user-123",
                "iat": now,
                "exp": now + 60,
            },
            SECRET,
            algorithm="HS256",
            headers={"kid": KEY_ID},
        )

        service.refresh(force=True)
        claims = await service.verify(token, audience="my-audience")
        print(f"Verified subject: {claims['sub']}")
    finally:
        server.shutdown()
        thread.join()


if __name__ == "__main__":
    asyncio.run(main())
```

The service performs JWKS discovery or fetch, validates the token
signature and issuer, and returns the decoded claims when verification
succeeds. Cache entries refresh automatically based on `cache_ttl_s` or
manually via `refresh(force=True)`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
# swarmauri_tokens_remoteoidc

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tokens_remoteoidc</strong></p>
<p align="center">Remote OIDC token verification service</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_remoteoidc/"><img alt="pypi: swarmauri_tokens_remoteoidc" src="https://img.shields.io/pypi/v/swarmauri_tokens_remoteoidc?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_remoteoidc/"><img alt="Monthly PyPI downloads: swarmauri_tokens_remoteoidc" src="https://img.shields.io/pypi/dm/swarmauri_tokens_remoteoidc?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/README.md"><img alt="README hits: swarmauri_tokens_remoteoidc" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_tokens_remoteoidc/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Remote OIDC token verification service for Swarmauri.

This package provides a verification-only token service that retrieves
JSON Web Key Sets (JWKS) from a remote OpenID Connect (OIDC) issuer and
validates JWTs in accordance with RFC 7517 and RFC 7519. It implements
`ITokenService` and exposes an entry point named
`RemoteOIDCTokenService`.

### Why This Package

`swarmauri_tokens_remoteoidc` isolates this responsibility: Remote OIDC token verification service. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/swarmauri_tokens_remoteoidc/__init__.py) exposes `RemoteOIDCTokenService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tokens_remoteoidc` when your integration needs remote OIDC token verification service. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Remote OIDC discovery with JWKS caching and conditional revalidation
  (ETag / Last-Modified).
- Audience and issuer validation with configurable clock-skew leeway.
- Optional extras for additional canonicalisation formats via the `cbor`
  extra.
- Manual refresh hook for cache priming plus a `jwks()` helper for
  introspection.
- Verification-only surface: `mint()` deliberately raises
  `NotImplementedError`.

### Non-Goals

`swarmauri_tokens_remoteoidc` owns remote OIDC token verification service. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `pyjwt`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tokens_remoteoidc
```
<!-- readme-standards:end installation.uv -->

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

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tokens_remoteoidc
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_tokens_remoteoidc
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tokens_remoteoidc
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_tokens_remoteoidc
```

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/docs/readme/quick_start.py).

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

        def log_message(
            self, format, *args
        ):  # pragma: no cover - quiet server
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
<!-- readme-standards:end example.quick-start -->

The snippet below boots a minimal HTTP server that hosts a JWKS
containing a symmetric key. It then mints a short-lived HS256 token and
verifies it using `RemoteOIDCTokenService`.


The service performs JWKS discovery or fetch, validates the token
signature and issuer, and returns the decoded claims when verification
succeeds. Cache entries refresh automatically based on `cache_ttl_s` or
manually via `refresh(force=True)`.

#### Expected Result

The example demonstrates the documented `swarmauri_tokens_remoteoidc` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/docs/readme/usage.py).

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

        def log_message(
            self, format, *args
        ):  # pragma: no cover - quiet server
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
<!-- readme-standards:end example.usage -->

1. Provide the expected OIDC issuer URL. Optionally override
   `jwks_url` to skip discovery when you already know the JWKS endpoint.
2. Call `refresh()` to prime caches when your process boots or after a
   rotation signal.
3. Await `verify()` with the JWT to validate signatures, issuer, and
   optional audience or nonce constraints.

### Configuration

Configure `swarmauri_tokens_remoteoidc` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/swarmauri_tokens_remoteoidc/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tokens_remoteoidc` source raises `NotImplementedError`, `RuntimeError`, `ValueError`, `jwt.ExpiredSignatureError`, `jwt.InvalidTokenError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tokens_remoteoidc` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `RemoteOIDCTokenService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tokens_remoteoidc` is located in `standards` and owns remote OIDC token verification service. Source-declared APIs include `RemoteOIDCTokenService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tokens_remoteoidc`.

Source-declared exports or types: `RemoteOIDCTokenService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/swarmauri_tokens_remoteoidc/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.tokens` → `remoteoidc` → `swarmauri_tokens_remoteoidc:RemoteOIDCTokenService`
- `swarmauri.tokens` → `RemoteOIDCTokenService` → `swarmauri_tokens_remoteoidc:RemoteOIDCTokenService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tokens_remoteoidc` are `swarmauri-core`, `swarmauri-base`, `pyjwt`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/swarmauri_tokens_remoteoidc/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tokens_remoteoidc` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tokens_remoteoidc`, use the source-declared public interfaces (`RemoteOIDCTokenService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tokens_remoteoidc` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tokens_remoteoidc`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/swarmauri_tokens_remoteoidc/__init__.py). The `swarmauri_tokens_remoteoidc` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tokens_remoteoidc` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tokens_remoteoidc` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/tests/example/test_readme_example.py)
- [tests/functional/test_remote_oidc_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/tests/functional/test_remote_oidc_functional.py)
- [tests/perf/test_remote_oidc_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/tests/perf/test_remote_oidc_perf.py)
- [tests/unit/test_rfc7517_jwks.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/tests/unit/test_rfc7517_jwks.py)
- [tests/unit/test_rfc7519_jwt.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/tests/unit/test_rfc7519_jwt.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tokens_remoteoidc` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/swarmauri_tokens_remoteoidc/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tokens_remoteoidc` provides remote OIDC token verification service; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tokens_remoteoidc`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/swarmauri_tokens_remoteoidc/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tokens_remoteoidc` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/swarmauri_tokens_remoteoidc/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/pyproject.toml) provide the supporting context for `swarmauri_tokens_remoteoidc`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tokens_remoteoidc](https://pypi.org/project/swarmauri_tokens_remoteoidc/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_tokens_remoteoidc` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_tokens_remoteoidc` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tokens_remoteoidc` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tokens_remoteoidc` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tokens_remoteoidc` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_remoteoidc/NOTICE) for attribution.
<!-- readme-standards:end notices -->

# swarmauri_tokens_dpopboundjwt

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tokens_dpopboundjwt</strong></p>
<p align="center">DPoP-bound JWT token service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_dpopboundjwt/"><img alt="pypi: swarmauri_tokens_dpopboundjwt" src="https://img.shields.io/pypi/v/swarmauri_tokens_dpopboundjwt"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_dpopboundjwt/"><img alt="Monthly PyPI downloads: swarmauri_tokens_dpopboundjwt" src="https://img.shields.io/pypi/dm/swarmauri_tokens_dpopboundjwt"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/README.md"><img alt="README hits: swarmauri_tokens_dpopboundjwt" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

DPoP-bound JSON Web Token (JWT) services for Swarmauri implementing [RFC 9449](https://www.rfc-editor.org/rfc/rfc9449) DPoP proof binding and [RFC 7638](https://www.rfc-editor.org/rfc/rfc7638) JWK thumbprints.

### Why This Package

`swarmauri_tokens_dpopboundjwt` isolates this responsibility: DPoP-bound JWT token service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/swarmauri_tokens_dpopboundjwt/__init__.py) exposes `DPoPBoundJWTTokenService`, `JWTTokenService`, `jwk_thumbprint_sha256`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tokens_dpopboundjwt` when your integration needs dPoP-bound JWT token service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Mints and verifies DPoP-bound JWT access tokens using the algorithms provided by the base `JWTTokenService` (`HS256`, `RS256`, `PS256`, `ES256`, `EdDSA`).
- Automatically injects the RFC 7638 thumbprint into the `cnf.jkt` claim when the DPoP context exposes the caller's public JWK.
- Enforces DPoP proof validation by checking the `dpop+jwt` header type, verifying the proof signature against the embedded JWK, and binding the HTTP method/URI, `iat`, and optional nonce (`proof_max_age_s` controls the allowed clock skew).
- Accepts an optional `replay_check(jti)` callback to harden against proof re-use and a `dpop_ctx_getter` to integrate with request-scoped metadata providers.
- Compatible with the `JWTTokenService` surface for issuer, subject, audience, scope, key selection, and header overrides.

### Non-Goals

`swarmauri_tokens_dpopboundjwt` owns dPoP-bound JWT token service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `pyjwt`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tokens_dpopboundjwt
```
<!-- readme-standards:end installation.uv -->

```bash
uv add swarmauri_tokens_dpopboundjwt
```

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tokens_dpopboundjwt
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_tokens_dpopboundjwt
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tokens_dpopboundjwt
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_tokens_dpopboundjwt
```

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/docs/readme/quick_start.py).

```python
# README example: mint and verify a DPoP-bound JWT
import asyncio
import json
import os
import time
import uuid
from typing import Any, Iterable, Mapping, Optional

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from jwt import algorithms

from swarmauri_core.crypto.types import (
    ExportPolicy,
    JWAAlg,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_tokens_dpopboundjwt import DPoPBoundJWTTokenService


class StaticKeyProvider(IKeyProvider):
    """Minimal symmetric key provider suitable for examples/tests."""

    def __init__(self, secret: bytes, kid: str = "default") -> None:
        self._kid = kid
        self._secret = secret
        self._ref = KeyRef(
            kid=kid,
            version=1,
            type=KeyType.SYMMETRIC,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=secret,
        )

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {"algs": ("HS256",)}

    async def create_key(
        self, spec: Any
    ):  # pragma: no cover - unused in example
        raise NotImplementedError

    async def import_key(
        self, spec: Any, material: bytes, *, public: bytes | None = None
    ):  # pragma: no cover - unused in example
        raise NotImplementedError

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ):  # pragma: no cover - unused in example
        raise NotImplementedError

    async def destroy_key(
        self, kid: str, version: Optional[int] = None
    ) -> bool:  # pragma: no cover - unused in example
        return False

    async def get_key(
        self,
        kid: str,
        version: Optional[int] = None,
        *,
        include_secret: bool = False,
    ) -> KeyRef:
        return self._ref

    async def list_versions(
        self, kid: str
    ) -> tuple[int, ...]:  # pragma: no cover
        return (self._ref.version,)

    async def get_public_jwk(  # pragma: no cover - unused in example
        self, kid: str, version: Optional[int] = None
    ) -> dict:
        raise NotImplementedError

    async def jwks(  # pragma: no cover - unused in example
        self, *, prefix_kids: Optional[str] = None
    ) -> dict:
        raise NotImplementedError

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - unused
        return os.urandom(n)

    async def hkdf(  # pragma: no cover - unused in example
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:
        raise NotImplementedError


async def main() -> None:
    key_provider = StaticKeyProvider(b"super-secret-signing-key")
    request_context: dict[str, object] = {}

    def get_ctx() -> dict[str, object]:
        return request_context

    service = DPoPBoundJWTTokenService(
        key_provider,
        default_issuer="https://issuer.test",
        dpop_ctx_getter=get_ctx,
        proof_max_age_s=300,
    )

    # Client presents the public key when the token is minted so we can bind cnf.jkt
    dpop_private_key = ec.generate_private_key(ec.SECP256R1())
    jwk_public = json.loads(
        algorithms.ECAlgorithm.to_jwk(dpop_private_key.public_key())
    )

    request_context.update({"jwk": jwk_public})

    access_token = await service.mint(
        {"sub": "alice@example.com"},
        alg=JWAAlg.HS256,
        audience="https://api.example.test",
        scope="read:messages",
    )

    # Incoming request carries a DPoP proof signed with the same key material
    htu = "https://api.example.test/resource"
    htm = "GET"
    nonce = "server-provided-nonce"
    proof_claims = {
        "htu": htu,
        "htm": htm,
        "iat": int(time.time()),
        "jti": str(uuid.uuid4()),
        "nonce": nonce,
    }
    proof_headers = {"typ": "dpop+jwt", "jwk": jwk_public}
    proof_jwt = jwt.encode(
        proof_claims,
        dpop_private_key,
        algorithm="ES256",
        headers=proof_headers,
    )

    request_context.update(
        {
            "proof": proof_jwt,
            "htu": htu,
            "htm": htm,
            "nonce": nonce,
        }
    )

    verified_claims = await service.verify(
        access_token, audience="https://api.example.test"
    )
    print("Verified subject:", verified_claims["sub"])
    print("Bound JWK thumbprint:", verified_claims["cnf"]["jkt"])


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tokens_dpopboundjwt` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/docs/readme/usage.py).

```python
# README example: mint and verify a DPoP-bound JWT
import asyncio
import json
import os
import time
import uuid
from typing import Any, Iterable, Mapping, Optional

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from jwt import algorithms

from swarmauri_core.crypto.types import (
    ExportPolicy,
    JWAAlg,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_tokens_dpopboundjwt import DPoPBoundJWTTokenService


class StaticKeyProvider(IKeyProvider):
    """Minimal symmetric key provider suitable for examples/tests."""

    def __init__(self, secret: bytes, kid: str = "default") -> None:
        self._kid = kid
        self._secret = secret
        self._ref = KeyRef(
            kid=kid,
            version=1,
            type=KeyType.SYMMETRIC,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=secret,
        )

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {"algs": ("HS256",)}

    async def create_key(
        self, spec: Any
    ):  # pragma: no cover - unused in example
        raise NotImplementedError

    async def import_key(
        self, spec: Any, material: bytes, *, public: bytes | None = None
    ):  # pragma: no cover - unused in example
        raise NotImplementedError

    async def rotate_key(
        self, kid: str, *, spec_overrides: Optional[dict] = None
    ):  # pragma: no cover - unused in example
        raise NotImplementedError

    async def destroy_key(
        self, kid: str, version: Optional[int] = None
    ) -> bool:  # pragma: no cover - unused in example
        return False

    async def get_key(
        self,
        kid: str,
        version: Optional[int] = None,
        *,
        include_secret: bool = False,
    ) -> KeyRef:
        return self._ref

    async def list_versions(
        self, kid: str
    ) -> tuple[int, ...]:  # pragma: no cover
        return (self._ref.version,)

    async def get_public_jwk(  # pragma: no cover - unused in example
        self, kid: str, version: Optional[int] = None
    ) -> dict:
        raise NotImplementedError

    async def jwks(  # pragma: no cover - unused in example
        self, *, prefix_kids: Optional[str] = None
    ) -> dict:
        raise NotImplementedError

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - unused
        return os.urandom(n)

    async def hkdf(  # pragma: no cover - unused in example
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:
        raise NotImplementedError


async def main() -> None:
    key_provider = StaticKeyProvider(b"super-secret-signing-key")
    request_context: dict[str, object] = {}

    def get_ctx() -> dict[str, object]:
        return request_context

    service = DPoPBoundJWTTokenService(
        key_provider,
        default_issuer="https://issuer.test",
        dpop_ctx_getter=get_ctx,
        proof_max_age_s=300,
    )

    # Client presents the public key when the token is minted so we can bind cnf.jkt
    dpop_private_key = ec.generate_private_key(ec.SECP256R1())
    jwk_public = json.loads(
        algorithms.ECAlgorithm.to_jwk(dpop_private_key.public_key())
    )

    request_context.update({"jwk": jwk_public})

    access_token = await service.mint(
        {"sub": "alice@example.com"},
        alg=JWAAlg.HS256,
        audience="https://api.example.test",
        scope="read:messages",
    )

    # Incoming request carries a DPoP proof signed with the same key material
    htu = "https://api.example.test/resource"
    htm = "GET"
    nonce = "server-provided-nonce"
    proof_claims = {
        "htu": htu,
        "htm": htm,
        "iat": int(time.time()),
        "jti": str(uuid.uuid4()),
        "nonce": nonce,
    }
    proof_headers = {"typ": "dpop+jwt", "jwk": jwk_public}
    proof_jwt = jwt.encode(
        proof_claims,
        dpop_private_key,
        algorithm="ES256",
        headers=proof_headers,
    )

    request_context.update(
        {
            "proof": proof_jwt,
            "htu": htu,
            "htm": htm,
            "nonce": nonce,
        }
    )

    verified_claims = await service.verify(
        access_token, audience="https://api.example.test"
    )
    print("Verified subject:", verified_claims["sub"])
    print("Bound JWK thumbprint:", verified_claims["cnf"]["jkt"])


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

**DPoP context expectations**

`DPoPBoundJWTTokenService` extends `JWTTokenService` and requires request context in order to bind and verify DPoP proofs. Supply a callable via `dpop_ctx_getter` that returns a mapping with the following keys:

- `jwk`: optional public JWK exposed during minting to automatically populate `cnf.jkt`.
- `proof`: the DPoP proof JWT received with a request.
- `htm`: HTTP method used for the protected resource request.
- `htu`: absolute HTTP URI for the protected resource request.
- `nonce`: optional server-provided nonce that, when present, must match the proof.

Set `enforce_proof=False` only when you intentionally want to accept tokens without a proof (for example during incremental rollout).

**Example: mint and verify a DPoP-bound JWT**

### Configuration

Configure `swarmauri_tokens_dpopboundjwt` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/swarmauri_tokens_dpopboundjwt/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tokens_dpopboundjwt` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tokens_dpopboundjwt` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `DPoPBoundJWTTokenService`, `JWTTokenService`, `jwk_thumbprint_sha256`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tokens_dpopboundjwt` is located in `standards` and owns dPoP-bound JWT token service for Swarmauri. Source-declared APIs include `DPoPBoundJWTTokenService`, `JWTTokenService`, `jwk_thumbprint_sha256`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tokens_dpopboundjwt`.

Source-declared exports or types: `DPoPBoundJWTTokenService`, `JWTTokenService`, `jwk_thumbprint_sha256`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/swarmauri_tokens_dpopboundjwt/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tokens` → `DPoPBoundJWTTokenService` → `swarmauri_tokens_dpopboundjwt:DPoPBoundJWTTokenService`
<!-- readme-standards:end entry-points -->

The service registers under the `swarmauri.tokens` entry point as `DPoPBoundJWTTokenService`.

A plain `JWTTokenService` is also exported for cases where DPoP binding is not required.

### Injected Dependencies

The direct installation dependencies of `swarmauri_tokens_dpopboundjwt` are `swarmauri-core`, `swarmauri-base`, `pyjwt`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/swarmauri_tokens_dpopboundjwt/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tokens_dpopboundjwt` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tokens_dpopboundjwt`, use the source-declared public interfaces (`DPoPBoundJWTTokenService`, `JWTTokenService`, `jwk_thumbprint_sha256`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tokens_dpopboundjwt` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tokens_dpopboundjwt`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/swarmauri_tokens_dpopboundjwt/__init__.py). The `swarmauri_tokens_dpopboundjwt` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tokens_dpopboundjwt` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tokens_dpopboundjwt` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/tests/test_readme_example.py)
- [tests/functional/test_rfc9449_dpop_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/tests/functional/test_rfc9449_dpop_functional.py)
- [tests/perf/test_dpop_verify_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/tests/perf/test_dpop_verify_perf.py)
- [tests/unit/test_rfc7638_thumbprint_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/tests/unit/test_rfc7638_thumbprint_unit.py)
- [tests/unit/test_rfc9449_compliance_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/tests/unit/test_rfc9449_compliance_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tokens_dpopboundjwt` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/swarmauri_tokens_dpopboundjwt/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tokens_dpopboundjwt` provides dPoP-bound JWT token service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tokens_dpopboundjwt`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/swarmauri_tokens_dpopboundjwt/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tokens_dpopboundjwt` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/swarmauri_tokens_dpopboundjwt/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/pyproject.toml) provide the supporting context for `swarmauri_tokens_dpopboundjwt`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tokens_dpopboundjwt](https://pypi.org/project/swarmauri_tokens_dpopboundjwt/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_tokens_dpopboundjwt` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_tokens_dpopboundjwt` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tokens_dpopboundjwt` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tokens_dpopboundjwt` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tokens_dpopboundjwt` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_dpopboundjwt/NOTICE) for attribution.
<!-- readme-standards:end notices -->

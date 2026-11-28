# swarmauri_tokens_jwt

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tokens_jwt</strong></p>
<p align="center">JWT token service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_jwt/"><img alt="pypi: swarmauri_tokens_jwt" src="https://img.shields.io/pypi/v/swarmauri_tokens_jwt?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_jwt/"><img alt="Monthly PyPI downloads: swarmauri_tokens_jwt" src="https://img.shields.io/pypi/dm/swarmauri_tokens_jwt?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/README.md"><img alt="README hits: swarmauri_tokens_jwt" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_tokens_jwt/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

A standard JWT token service for the Swarmauri framework. This service
implements minting and verifying JSON Web Tokens and exposes a JWKS
endpoint for public key discovery.

### Why This Package

`swarmauri_tokens_jwt` isolates this responsibility: JWT token service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/swarmauri_tokens_jwt/__init__.py) exposes `JWTClaimsValidationError`, `JWTClaimsValidator`, `JWTTokenService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tokens_jwt` when your integration needs jWT token service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Mint and verify JWS/JWT tokens backed by any :class:`~swarmauri_core.key_providers.IKeyProvider`
- Supports algorithms like **HS256**, **RS256**, **ES256**, **PS256** and **EdDSA**
- Adds standard temporal claims (`iat`, `nbf`, and optional `exp`) plus issuer,
  subject, audience and scope defaults when minting tokens
- Validates expiration, not-before, issuer and audience claims during
  verification
- Publishes a JWKS endpoint for public key discovery through your key provider
- Exposes `JWTClaimsValidator` for transport-independent required-claim,
  temporal, issuer, audience, scope, role, and custom claim policy
- Install the optional ``cryptography`` dependency to enable RSA, ECDSA and
  EdDSA signing keys

### Non-Goals

`swarmauri_tokens_jwt` owns jWT token service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-signing-jws`. Read the example’s inputs and service requirements before execution.

### Installation

Install the service with your preferred Python packaging tool:

```bash
pip install swarmauri_tokens_jwt
```

```bash
poetry add swarmauri_tokens_jwt
```

```bash
uv pip install swarmauri_tokens_jwt
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tokens_jwt
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tokens_jwt
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tokens_jwt
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/docs/readme/quick_start.py).

```python
import asyncio
import base64
from swarmauri_tokens_jwt import JWTTokenService
from swarmauri_core.key_providers import (
    ExportPolicy,
    IKeyProvider,
    KeyRef,
    KeyUse,
)
from swarmauri_core.crypto.types import JWAAlg, KeyType


class InMemoryKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.secret = b"secret"
        self.kid = "sym"
        self.version = 1

    def supports(self) -> dict[str, list[str]]:
        return {}

    async def create_key(self, spec):
        raise NotImplementedError

    async def import_key(self, spec, material, *, public=None):
        raise NotImplementedError

    async def rotate_key(self, kid, *, spec_overrides=None):
        raise NotImplementedError

    async def destroy_key(self, kid, version=None) -> bool:
        return False

    async def get_key(
        self, kid, version=None, *, include_secret=False
    ) -> KeyRef:
        material = self.secret if include_secret else None
        return KeyRef(
            kid=self.kid,
            version=self.version,
            type=KeyType.OPAQUE,
            uses=(KeyUse.SIGN,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=material,
        )

    async def list_versions(self, kid):
        return (self.version,)

    async def get_public_jwk(self, kid, version=None):
        return {}

    async def jwks(self) -> dict:
        k = base64.urlsafe_b64encode(self.secret).rstrip(b"=").decode()
        return {
            "keys": [
                {"kty": "oct", "kid": f"{self.kid}.{self.version}", "k": k}
            ]
        }

    async def random_bytes(self, n: int) -> bytes:
        return b"\x00" * n

    async def hkdf(
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:
        return b"\x00" * length


async def main() -> None:
    svc = JWTTokenService(InMemoryKeyProvider(), default_issuer="issuer")
    token = await svc.mint(
        {"sub": "alice"},
        alg=JWAAlg.HS256,
        kid="sym",
        lifetime_s=600,  # override the default one-hour lifetime if needed
    )
    claims = await svc.verify(token, issuer="issuer")
    assert claims["sub"] == "alice"


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tokens_jwt` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/docs/readme/usage.py).

```python
import asyncio
import base64
from swarmauri_tokens_jwt import JWTTokenService
from swarmauri_core.key_providers import (
    ExportPolicy,
    IKeyProvider,
    KeyRef,
    KeyUse,
)
from swarmauri_core.crypto.types import JWAAlg, KeyType


class InMemoryKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.secret = b"secret"
        self.kid = "sym"
        self.version = 1

    def supports(self) -> dict[str, list[str]]:
        return {}

    async def create_key(self, spec):
        raise NotImplementedError

    async def import_key(self, spec, material, *, public=None):
        raise NotImplementedError

    async def rotate_key(self, kid, *, spec_overrides=None):
        raise NotImplementedError

    async def destroy_key(self, kid, version=None) -> bool:
        return False

    async def get_key(
        self, kid, version=None, *, include_secret=False
    ) -> KeyRef:
        material = self.secret if include_secret else None
        return KeyRef(
            kid=self.kid,
            version=self.version,
            type=KeyType.OPAQUE,
            uses=(KeyUse.SIGN,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=material,
        )

    async def list_versions(self, kid):
        return (self.version,)

    async def get_public_jwk(self, kid, version=None):
        return {}

    async def jwks(self) -> dict:
        k = base64.urlsafe_b64encode(self.secret).rstrip(b"=").decode()
        return {
            "keys": [
                {"kty": "oct", "kid": f"{self.kid}.{self.version}", "k": k}
            ]
        }

    async def random_bytes(self, n: int) -> bytes:
        return b"\x00" * n

    async def hkdf(
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:
        return b"\x00" * length


async def main() -> None:
    svc = JWTTokenService(InMemoryKeyProvider(), default_issuer="issuer")
    token = await svc.mint(
        {"sub": "alice"},
        alg=JWAAlg.HS256,
        kid="sym",
        lifetime_s=600,  # override the default one-hour lifetime if needed
    )
    claims = await svc.verify(token, issuer="issuer")
    assert claims["sub"] == "alice"


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

`JWTTokenService` requires an asynchronous `IKeyProvider` to supply signing
material. The example below shows how to mint and verify a symmetric **HS256**
token using a minimal in-memory key provider.


`verify` retrieves the JSON Web Key Set from the provider and enforces
expiration, not-before, issuer and audience checks before returning the decoded
claims. Expose the service's :meth:`jwks` coroutine to publish the active public
keys from your provider.

Use `JWTClaimsValidator` when claims have already been authenticated by a JWS
verifier and need application policy independent of HTTP middleware:

```python
from swarmauri_tokens_jwt import JWTClaimsValidator

validator = JWTClaimsValidator(
    required_claims={"sub", "iat", "exp"},
    issuer="https://identity.example.com",
    audience="swarmauri-api",
    required_scopes={"documents:read"},
)
claims = validator.validate(authenticated_claims)
```

The service also supports asymmetric algorithms such as **RS256**, **ES256** and
**EdDSA** when the key provider exposes the appropriate keys. See the
docstrings in :mod:`swarmauri_tokens_jwt` for additional details on the API
surface.

### Configuration

Configure `swarmauri_tokens_jwt` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/swarmauri_tokens_jwt/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tokens_jwt` source raises `JWTClaimsValidationError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tokens_jwt` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `JWTClaimsValidationError`, `JWTClaimsValidator`, `JWTTokenService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tokens_jwt` is located in `standards` and owns jWT token service for Swarmauri. Source-declared APIs include `JWTClaimsValidationError`, `JWTClaimsValidator`, `JWTTokenService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tokens_jwt`.

Source-declared exports or types: `JWTClaimsValidationError`, `JWTClaimsValidator`, `JWTTokenService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/swarmauri_tokens_jwt/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.tokens` → `jwt` → `swarmauri_tokens_jwt:JWTTokenService`
- `swarmauri.tokens` → `JWTTokenService` → `swarmauri_tokens_jwt:JWTTokenService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tokens_jwt` are `swarmauri-core`, `swarmauri-base`, `swarmauri-signing-jws`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/swarmauri_tokens_jwt/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_middleware_jwt`, `swarmauri_workflow_documentassistant`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_tokens_jwt`, use the source-declared public interfaces (`JWTClaimsValidationError`, `JWTClaimsValidator`, `JWTTokenService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tokens_jwt` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tokens_jwt`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/swarmauri_tokens_jwt/__init__.py). The `swarmauri_tokens_jwt` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tokens_jwt` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tokens_jwt` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/functional/test_jwttokenservice_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/tests/functional/test_jwttokenservice_functional.py)
- [tests/perf/test_jwttokenservice_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/tests/perf/test_jwttokenservice_perf.py)
- [tests/unit/test_jwttokenservice_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/tests/unit/test_jwttokenservice_unit.py)
- [tests/unit/test_jwt_claims_validator.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/tests/unit/test_jwt_claims_validator.py)
- [tests/unit/test_keys_import_compat.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/tests/unit/test_keys_import_compat.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tokens_jwt` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/swarmauri_tokens_jwt/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tokens_jwt` provides jWT token service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tokens_jwt`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/swarmauri_tokens_jwt/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tokens_jwt` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/swarmauri_tokens_jwt/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/pyproject.toml) provide the supporting context for `swarmauri_tokens_jwt`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_signing_jws](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/README.md): Composite JWS signer/verifier for Swarmauri

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tokens_jwt](https://pypi.org/project/swarmauri_tokens_jwt/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_tokens_jwt` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_tokens_jwt` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tokens_jwt` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tokens_jwt` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tokens_jwt` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_jwt/NOTICE) for attribution.
<!-- readme-standards:end notices -->

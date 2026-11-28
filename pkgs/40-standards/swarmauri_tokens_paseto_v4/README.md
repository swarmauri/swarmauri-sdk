# swarmauri_tokens_paseto_v4

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tokens_paseto_v4</strong></p>
<p align="center">PASETO v4 token service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_paseto_v4/"><img alt="pypi: swarmauri_tokens_paseto_v4" src="https://img.shields.io/pypi/v/swarmauri_tokens_paseto_v4?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_paseto_v4/"><img alt="Monthly PyPI downloads: swarmauri_tokens_paseto_v4" src="https://img.shields.io/pypi/dm/swarmauri_tokens_paseto_v4?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/README.md"><img alt="README hits: swarmauri_tokens_paseto_v4" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_tokens_paseto_v4/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`PasetoV4TokenService` provides `v4.public` signing and `v4.local`
encryption for Swarmauri-compatible applications using the
[`pyseto`](https://pypi.org/project/pyseto/) reference implementation.  The
service implements the `ITokenService` interface and validates standard JWT
claims (`exp`, `nbf`, `iat`, `iss`, and `aud`) when verifying tokens.

### Why This Package

`swarmauri_tokens_paseto_v4` isolates this responsibility: PASETO v4 token service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/swarmauri_tokens_paseto_v4/__init__.py) exposes `PasetoV4TokenService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tokens_paseto_v4` when your integration needs pASETO v4 token service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Ed25519 signing for `v4.public` operations using keys supplied by an
  `IKeyProvider` implementation.
- XChaCha20-Poly1305 encryption for `v4.local` tokens with symmetric keys.
- Automatic population of `iat` and `nbf` claims plus an optional `exp`
  derived from `lifetime_s`.
- Registered-claim validation during verification with configurable issuer and
  audience matching.
- Optional CBOR canonicalization of payloads via the `cbor` extra.
- Asynchronous API compatible with the broader Swarmauri token service
  ecosystem.

### Non-Goals

`swarmauri_tokens_paseto_v4` owns pASETO v4 token service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `pyseto`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_tokens_paseto_v4
```

```bash
poetry add swarmauri_tokens_paseto_v4
```

```bash
uv pip install swarmauri_tokens_paseto_v4
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tokens_paseto_v4
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tokens_paseto_v4
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tokens_paseto_v4
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/docs/readme/quick_start.py).

```python
import asyncio
import base64
import os
from typing import Iterable, Mapping, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from swarmauri_tokens_paseto_v4 import PasetoV4TokenService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_core.key_providers.types import KeyAlg


class InMemoryKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self._sk = Ed25519PrivateKey.generate()
        self._sym = os.urandom(32)
        self._refs = {
            "ed1": KeyRef(
                kid="ed1",
                version=1,
                type=KeyType.ED25519,
                uses=(KeyUse.SIGN, KeyUse.VERIFY),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=self._sk.private_bytes(
                    Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
                ),
                public=self._sk.public_key().public_bytes(
                    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
                ),
                tags={"alg": KeyAlg.ED25519.value},
            ),
            "sym1": KeyRef(
                kid="sym1",
                version=1,
                type=KeyType.SYMMETRIC,
                uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=self._sym,
                public=None,
                tags={"alg": KeyAlg.AES256_GCM.value},
            ),
        }
        self._jwks = {
            "keys": [
                {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "kid": "ed1",
                    "x": base64.urlsafe_b64encode(
                        self._sk.public_key().public_bytes(
                            Encoding.Raw, PublicFormat.Raw
                        )
                    )
                    .rstrip(b"=")
                    .decode("ascii"),
                }
            ]
        }

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {}

    async def create_key(
        self, spec
    ):  # pragma: no cover - unused in the example
        raise NotImplementedError

    async def import_key(
        self, spec, material, *, public=None
    ):  # pragma: no cover
        raise NotImplementedError

    async def rotate_key(
        self, kid, *, spec_overrides=None
    ):  # pragma: no cover
        raise NotImplementedError

    async def destroy_key(self, kid, version=None):  # pragma: no cover
        raise NotImplementedError

    async def get_key(self, kid, version=None, include_secret=False):
        return self._refs[kid]

    async def list_versions(self, kid):  # pragma: no cover - unused
        return (1,)

    async def get_public_jwk(self, kid, version=None):  # pragma: no cover
        return self._jwks["keys"][0]

    async def jwks(self, *, prefix_kids: Optional[str] = None):
        return self._jwks

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - unused
        return os.urandom(n)

    async def hkdf(
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:  # pragma: no cover - unused
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)


async def main() -> None:
    provider = InMemoryKeyProvider()
    service = PasetoV4TokenService(
        provider,
        default_issuer="auth.example",
        local_kids=["sym1"],
    )

    public_token = await service.mint(
        {"role": "admin"},
        alg="v4.public",
        kid="ed1",
        audience="my-service",
    )
    verified_public = await service.verify(public_token, audience="my-service")
    print("Verified role:", verified_public["role"])

    local_token = await service.mint(
        {"feature": "beta"},
        alg="v4.local",
        kid="sym1",
    )
    verified_local = await service.verify(local_token)
    print("Local feature flag:", verified_local["feature"])


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tokens_paseto_v4` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/docs/readme/usage.py).

```python
import asyncio
import base64
import os
from typing import Iterable, Mapping, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from swarmauri_tokens_paseto_v4 import PasetoV4TokenService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider
from swarmauri_core.key_providers.types import KeyAlg


class InMemoryKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self._sk = Ed25519PrivateKey.generate()
        self._sym = os.urandom(32)
        self._refs = {
            "ed1": KeyRef(
                kid="ed1",
                version=1,
                type=KeyType.ED25519,
                uses=(KeyUse.SIGN, KeyUse.VERIFY),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=self._sk.private_bytes(
                    Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
                ),
                public=self._sk.public_key().public_bytes(
                    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
                ),
                tags={"alg": KeyAlg.ED25519.value},
            ),
            "sym1": KeyRef(
                kid="sym1",
                version=1,
                type=KeyType.SYMMETRIC,
                uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                material=self._sym,
                public=None,
                tags={"alg": KeyAlg.AES256_GCM.value},
            ),
        }
        self._jwks = {
            "keys": [
                {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "kid": "ed1",
                    "x": base64.urlsafe_b64encode(
                        self._sk.public_key().public_bytes(
                            Encoding.Raw, PublicFormat.Raw
                        )
                    )
                    .rstrip(b"=")
                    .decode("ascii"),
                }
            ]
        }

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {}

    async def create_key(
        self, spec
    ):  # pragma: no cover - unused in the example
        raise NotImplementedError

    async def import_key(
        self, spec, material, *, public=None
    ):  # pragma: no cover
        raise NotImplementedError

    async def rotate_key(
        self, kid, *, spec_overrides=None
    ):  # pragma: no cover
        raise NotImplementedError

    async def destroy_key(self, kid, version=None):  # pragma: no cover
        raise NotImplementedError

    async def get_key(self, kid, version=None, include_secret=False):
        return self._refs[kid]

    async def list_versions(self, kid):  # pragma: no cover - unused
        return (1,)

    async def get_public_jwk(self, kid, version=None):  # pragma: no cover
        return self._jwks["keys"][0]

    async def jwks(self, *, prefix_kids: Optional[str] = None):
        return self._jwks

    async def random_bytes(self, n: int) -> bytes:  # pragma: no cover - unused
        return os.urandom(n)

    async def hkdf(
        self, ikm: bytes, *, salt: bytes, info: bytes, length: int
    ) -> bytes:  # pragma: no cover - unused
        return HKDF(
            algorithm=hashes.SHA256(), length=length, salt=salt, info=info
        ).derive(ikm)


async def main() -> None:
    provider = InMemoryKeyProvider()
    service = PasetoV4TokenService(
        provider,
        default_issuer="auth.example",
        local_kids=["sym1"],
    )

    public_token = await service.mint(
        {"role": "admin"},
        alg="v4.public",
        kid="ed1",
        audience="my-service",
    )
    verified_public = await service.verify(public_token, audience="my-service")
    print("Verified role:", verified_public["role"])

    local_token = await service.mint(
        {"feature": "beta"},
        alg="v4.local",
        kid="sym1",
    )
    verified_local = await service.verify(local_token)
    print("Local feature flag:", verified_local["feature"])


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

The example below spins up an in-memory key provider with one Ed25519 signing
key and one symmetric key, mints both `v4.public` and `v4.local` tokens, and
verifies their contents.


Running the script prints the verified claim values for both the signed and the
encrypted token.  In a production deployment you would connect the token
service to your own `IKeyProvider` implementation so the keys can be rotated or
backed by a hardware security module.

### Configuration

Configure `swarmauri_tokens_paseto_v4` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/swarmauri_tokens_paseto_v4/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tokens_paseto_v4` source raises `ImportError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tokens_paseto_v4` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `PasetoV4TokenService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tokens_paseto_v4` is located in `standards` and owns pASETO v4 token service for Swarmauri. Source-declared APIs include `PasetoV4TokenService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tokens_paseto_v4`.

Source-declared exports or types: `PasetoV4TokenService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/swarmauri_tokens_paseto_v4/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.tokens` → `paseto_v4` → `swarmauri_tokens_paseto_v4:PasetoV4TokenService`
- `swarmauri.tokens` → `PasetoV4TokenService` → `swarmauri_tokens_paseto_v4:PasetoV4TokenService`
<!-- readme-standards:end entry-points -->

The package exposes `PasetoV4TokenService` under the `swarmauri.tokens`
setuptools entry point group, making it discoverable by other Swarmauri
components.

### Injected Dependencies

The direct installation dependencies of `swarmauri_tokens_paseto_v4` are `swarmauri-core`, `swarmauri-base`, `pyseto`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/swarmauri_tokens_paseto_v4/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tokens_paseto_v4` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tokens_paseto_v4`, use the source-declared public interfaces (`PasetoV4TokenService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tokens_paseto_v4` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tokens_paseto_v4`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/swarmauri_tokens_paseto_v4/__init__.py). The `swarmauri_tokens_paseto_v4` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tokens_paseto_v4` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tokens_paseto_v4` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/tests/test_readme_example.py)
- [tests/functional/test_service_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/tests/functional/test_service_functional.py)
- [tests/perf/test_service_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/tests/perf/test_service_perf.py)
- [tests/unit/test_rfc7519_claims.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/tests/unit/test_rfc7519_claims.py)
- [tests/unit/test_service_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/tests/unit/test_service_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tokens_paseto_v4` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/swarmauri_tokens_paseto_v4/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tokens_paseto_v4` provides pASETO v4 token service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tokens_paseto_v4`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/swarmauri_tokens_paseto_v4/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tokens_paseto_v4` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/swarmauri_tokens_paseto_v4/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/pyproject.toml) provide the supporting context for `swarmauri_tokens_paseto_v4`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tokens_paseto_v4](https://pypi.org/project/swarmauri_tokens_paseto_v4/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_tokens_paseto_v4` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Key provider requirements**

`PasetoV4TokenService` delegates key management to an object implementing the
`IKeyProvider` interface from `swarmauri_core`.  The provider is expected to:

- Return an Ed25519 private key (PEM encoded) when `get_key` is called for
  `v4.public` signing operations.
- Return a 32-byte symmetric key for `v4.local` encryption and expose the
  corresponding key IDs through the service's `local_kids` parameter.
- Supply an Ed25519 JWK via `jwks()` so that public tokens can be verified
  without direct access to the signing key material.
- Optionally provide a default issuer, implicit assertions, and key rotation
  metadata using the `KeyRef` structure from `swarmauri_core`.

**Claim handling**

When minting a token the service merges your custom claim payload with a set of
registered defaults:

- `iat` (issued at) and `nbf` (not before) are populated with the current epoch
  time when not explicitly provided.
- `exp` (expiration) is derived from `lifetime_s` when supplied.
- `iss`, `sub`, `aud`, and `scope` claims are added when the corresponding
  keyword arguments are passed to `mint` or when a `default_issuer` is set on
  the service instance.

During verification the service ensures that tokens are not expired, are
currently valid, and that issuer and audience claims match the expectations you
supply.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tokens_paseto_v4` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tokens_paseto_v4` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tokens_paseto_v4` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tokens_paseto_v4/NOTICE) for attribution.
<!-- readme-standards:end notices -->

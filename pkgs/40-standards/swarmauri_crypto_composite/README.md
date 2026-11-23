# swarmauri_crypto_composite

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_crypto_composite</strong></p>
<p align="center">Algorithm-routing crypto provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_composite/"><img alt="pypi: swarmauri_crypto_composite" src="https://img.shields.io/pypi/v/swarmauri_crypto_composite?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_composite/"><img alt="Monthly PyPI downloads: swarmauri_crypto_composite" src="https://img.shields.io/pypi/dm/swarmauri_crypto_composite?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/README.md"><img alt="README hits: swarmauri_crypto_composite" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_crypto_composite/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_crypto_composite`: Algorithm-routing crypto provider for Swarmauri

### Why This Package

`swarmauri_crypto_composite` isolates this responsibility: Algorithm-routing crypto provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/swarmauri_crypto_composite/__init__.py) exposes `CompositeCrypto`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_crypto_composite` when your integration needs algorithm-routing crypto provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `CompositeCrypto`: Algorithm-routing crypto provider.

### Non-Goals

`swarmauri_crypto_composite` owns algorithm-routing crypto provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that best fits your workflow:

```bash
pip install swarmauri_crypto_composite
```

```bash
poetry add swarmauri_crypto_composite
```

```bash
uv add swarmauri_crypto_composite
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_crypto_composite
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_crypto_composite
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_crypto_composite
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/docs/readme/quick_start.py).

```python
"""Route crypto operations to a provider that supports the algorithm."""

import asyncio

from swarmauri_core.crypto.ICrypto import ICrypto
from swarmauri_core.crypto.types import (
    AEADCiphertext,
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_crypto_composite import CompositeCrypto


class DummyCrypto(ICrypto):
    def __init__(self, name: str, alg: str) -> None:
        self._name = name
        self._alg = alg

    def supports(self):
        return {"encrypt": (self._alg,)}

    async def encrypt(self, key, pt, *, alg=None, aad=None, nonce=None):
        return AEADCiphertext(
            kid="dummy",
            version=1,
            alg=alg or self._alg,
            nonce=b"",
            ct=self._name.encode(),
            tag=b"",
        )

    async def decrypt(
        self, key, ct, *, aad=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def wrap(
        self, kek, *, dek=None, wrap_alg=None, nonce=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def unwrap(self, kek, wrapped):  # pragma: no cover - demo only
        raise NotImplementedError

    async def seal(
        self, recipient, pt, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def unseal(
        self, recipient_priv, sealed, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def encaps(
        self, recipient, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def decaps(
        self, recipient_priv, encapsulated_key, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError


async def main() -> None:
    # Compose two providers that advertise different algorithms.
    chacha = DummyCrypto("chacha", "CHACHA20-POLY1305")
    aes = DummyCrypto("aes", "A256GCM")
    composite = CompositeCrypto([chacha, aes])

    key = KeyRef(
        kid="k",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ciphertext = await composite.encrypt(key, b"payload", alg="A256GCM")
    print(f"Selected provider: {ciphertext.ct.decode()}")


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_crypto_composite` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/docs/readme/usage.py).

```python
"""Route crypto operations to a provider that supports the algorithm."""

import asyncio

from swarmauri_core.crypto.ICrypto import ICrypto
from swarmauri_core.crypto.types import (
    AEADCiphertext,
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)
from swarmauri_crypto_composite import CompositeCrypto


class DummyCrypto(ICrypto):
    def __init__(self, name: str, alg: str) -> None:
        self._name = name
        self._alg = alg

    def supports(self):
        return {"encrypt": (self._alg,)}

    async def encrypt(self, key, pt, *, alg=None, aad=None, nonce=None):
        return AEADCiphertext(
            kid="dummy",
            version=1,
            alg=alg or self._alg,
            nonce=b"",
            ct=self._name.encode(),
            tag=b"",
        )

    async def decrypt(
        self, key, ct, *, aad=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def wrap(
        self, kek, *, dek=None, wrap_alg=None, nonce=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def unwrap(self, kek, wrapped):  # pragma: no cover - demo only
        raise NotImplementedError

    async def seal(
        self, recipient, pt, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def unseal(
        self, recipient_priv, sealed, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def encaps(
        self, recipient, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError

    async def decaps(
        self, recipient_priv, encapsulated_key, *, alg=None
    ):  # pragma: no cover - demo only
        raise NotImplementedError


async def main() -> None:
    # Compose two providers that advertise different algorithms.
    chacha = DummyCrypto("chacha", "CHACHA20-POLY1305")
    aes = DummyCrypto("aes", "A256GCM")
    composite = CompositeCrypto([chacha, aes])

    key = KeyRef(
        kid="k",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ciphertext = await composite.encrypt(key, b"payload", alg="A256GCM")
    print(f"Selected provider: {ciphertext.ct.decode()}")


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_crypto_composite` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/swarmauri_crypto_composite/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_crypto_composite` source raises `UnsupportedAlgorithm`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_crypto_composite` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CompositeCrypto`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_crypto_composite` is located in `standards` and owns algorithm-routing crypto provider for Swarmauri. Source-declared APIs include `CompositeCrypto`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_crypto_composite`.

Source-declared exports or types: `CompositeCrypto`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/swarmauri_crypto_composite/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.cryptos` → `composite` → `swarmauri_crypto_composite:CompositeCrypto`
- `swarmauri.cryptos` → `CompositeCrypto` → `swarmauri_crypto_composite:CompositeCrypto`
<!-- readme-standards:end entry-points -->

The provider is registered under the `swarmauri.cryptos` entry-point as `CompositeCrypto`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_crypto_composite` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/swarmauri_crypto_composite/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_crypto_composite` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_crypto_composite`, use the source-declared public interfaces (`CompositeCrypto`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_crypto_composite` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_crypto_composite`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/swarmauri_crypto_composite/__init__.py). The `swarmauri_crypto_composite` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_crypto_composite` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_crypto_composite` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_composite_crypto.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/tests/test_composite_crypto.py)
- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/tests/test_readme_example.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_crypto_composite` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/swarmauri_crypto_composite/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_crypto_composite` provides algorithm-routing crypto provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_crypto_composite`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/swarmauri_crypto_composite/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_crypto_composite` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/swarmauri_crypto_composite/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/pyproject.toml) provide the supporting context for `swarmauri_crypto_composite`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_crypto_composite](https://pypi.org/project/swarmauri_crypto_composite/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_crypto_composite` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Crypto Composite**

`CompositeCrypto` is an algorithm-routing crypto provider that delegates encryption
operations to the first child provider that advertises support for the requested
algorithm. Its behaviour is defined entirely by the wrapped providers:

- Aggregates each provider's `supports()` capabilities and removes duplicates.
- Normalises requested algorithms before routing so stylistic variants still match.
- Requires at least one child provider to be supplied at construction time.
- Exposes the full asynchronous `ICrypto` surface area (encrypt, wrap, seal, etc.).

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_crypto_composite` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_crypto_composite` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_crypto_composite` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_composite/NOTICE) for attribution.
<!-- readme-standards:end notices -->

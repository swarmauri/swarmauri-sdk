# swarmauri_keyprovider_hierarchical

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_keyprovider_hierarchical</strong></p>
<p align="center">Hierarchical key provider for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_hierarchical/"><img alt="pypi: swarmauri_keyprovider_hierarchical" src="https://img.shields.io/pypi/v/swarmauri_keyprovider_hierarchical"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_keyprovider_hierarchical/"><img alt="Monthly PyPI downloads: swarmauri_keyprovider_hierarchical" src="https://img.shields.io/pypi/dm/swarmauri_keyprovider_hierarchical"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/README.md"><img alt="README hits: swarmauri_keyprovider_hierarchical" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_keyprovider_hierarchical/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Plugin providing a policy-driven composite key provider capable of routing
key operations across multiple child providers. It implements the
`IKeyProvider` interface and exposes a single `HierarchicalKeyProvider`
class.

`HierarchicalKeyProvider` composes a mapping of named child providers and
routes every key operation to the correct child according to declarative
policies.  It offers:

- **Create/import routing** ? specify ordered [`CreateRule`](#routing-policy)
  objects that match key class, algorithm, usage, or export policy. The first
  rule that matches a `KeySpec` wins.
- **Automatic discovery** ? when looking up an unknown key identifier (KID)
  the provider probes each child until it finds the owning provider and caches
  the association for future calls.
- **Persistent indexing** ? optionally persist the learned KID ? provider map
  to JSON via the `index_file` argument so the routing cache survives process
  restarts.
- **Capability passthrough** ? rotate, destroy, list, JWKS, HKDF, and random
  byte requests are forwarded transparently to the owning (or designated)
  child provider. JWKS responses are merged across children while avoiding
  duplicate KIDs.
- **Heuristic fallback** ? if no policy matches a create/import request the
  provider falls back to sensible defaults: asymmetric keys prefer children
  named like KMS/PKCS#11, symmetric keys prefer local/file providers, and
  otherwise the first registered child is used.

### Why This Package

`swarmauri_keyprovider_hierarchical` isolates this responsibility: Hierarchical key provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/swarmauri_keyprovider_hierarchical/__init__.py) exposes `CreateRule`, `HierarchicalKeyProvider`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_keyprovider_hierarchical` when your integration needs hierarchical key provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `CreateRule`: Route selection rule for create/import.
- `HierarchicalKeyProvider`: A policy-driven composite IKeyProvider.

### Non-Goals

`swarmauri_keyprovider_hierarchical` owns hierarchical key provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-keyprovider-local`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the installer that matches your workflow.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_keyprovider_hierarchical
```
<!-- readme-standards:end installation.uv -->

```bash
uv venv  # create (or reuse) a virtual environment
source .venv/bin/activate
uv pip install swarmauri_keyprovider_hierarchical
```

If you are already inside a uv-managed environment you can shorten the last
two steps to `uv pip install swarmauri_keyprovider_hierarchical`.

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_keyprovider_hierarchical
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_keyprovider_hierarchical
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_keyprovider_hierarchical
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_keyprovider_hierarchical
```

### Quick Start

The example below wires two `LocalKeyProvider` instances behind a
`HierarchicalKeyProvider`. Symmetric keys are routed to a local provider while
asymmetric keys land on a provider named `kms`. The composite provider also
serves random bytes and JWKS responses for all children.

<!-- example-start -->
<!-- example-end -->

Running the script prints the generated key identifiers, confirms the random
token length, and shows how many public keys were merged into the JWKS
document.

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/docs/readme/quick_start.py).

```python
"""Create keys across multiple providers with policy-driven routing."""

import asyncio

from swarmauri_keyprovider_hierarchical import (
    HierarchicalKeyProvider,
    CreateRule,
)
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
    KeyUse,
)


async def main() -> None:
    children = {
        "kms": LocalKeyProvider(),
        "local": LocalKeyProvider(),
    }
    provider = HierarchicalKeyProvider(
        children,
        create_policy=[
            CreateRule(provider="kms", klass=KeyClass.asymmetric),
            CreateRule(provider="local", klass=KeyClass.symmetric),
        ],
        randomness_provider="local",  # designate a child for random_bytes
    )

    symmetric_spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    asymmetric_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )

    symmetric_ref = await provider.create_key(symmetric_spec)
    asymmetric_ref = await provider.create_key(asymmetric_spec)
    random_token = await provider.random_bytes(16)
    jwks = await provider.jwks()

    print(f"Symmetric key kid: {symmetric_ref.kid}")
    print(f"Asymmetric key kid: {asymmetric_ref.kid}")
    print(f"Random token length: {len(random_token)} bytes")
    print(f"JWKS entries: {len(jwks['keys'])}")


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_keyprovider_hierarchical` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/docs/readme/usage.py).

```python
"""Create keys across multiple providers with policy-driven routing."""

import asyncio

from swarmauri_keyprovider_hierarchical import (
    HierarchicalKeyProvider,
    CreateRule,
)
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import (
    ExportPolicy,
    KeyAlg,
    KeyClass,
    KeySpec,
    KeyUse,
)


async def main() -> None:
    children = {
        "kms": LocalKeyProvider(),
        "local": LocalKeyProvider(),
    }
    provider = HierarchicalKeyProvider(
        children,
        create_policy=[
            CreateRule(provider="kms", klass=KeyClass.asymmetric),
            CreateRule(provider="local", klass=KeyClass.symmetric),
        ],
        randomness_provider="local",  # designate a child for random_bytes
    )

    symmetric_spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    asymmetric_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )

    symmetric_ref = await provider.create_key(symmetric_spec)
    asymmetric_ref = await provider.create_key(asymmetric_spec)
    random_token = await provider.random_bytes(16)
    jwks = await provider.jwks()

    print(f"Symmetric key kid: {symmetric_ref.kid}")
    print(f"Asymmetric key kid: {asymmetric_ref.kid}")
    print(f"Random token length: {len(random_token)} bytes")
    print(f"JWKS entries: {len(jwks['keys'])}")


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_keyprovider_hierarchical` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/swarmauri_keyprovider_hierarchical/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_keyprovider_hierarchical` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_keyprovider_hierarchical` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CreateRule`, `HierarchicalKeyProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_keyprovider_hierarchical` is located in `standards` and owns hierarchical key provider for Swarmauri. Source-declared APIs include `CreateRule`, `HierarchicalKeyProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_keyprovider_hierarchical`.

Source-declared exports or types: `CreateRule`, `HierarchicalKeyProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/swarmauri_keyprovider_hierarchical/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.key_providers` → `hierarchical` → `swarmauri_keyprovider_hierarchical.HierarchicalKeyProvider:HierarchicalKeyProvider`
- `swarmauri.key_providers` → `HierarchicalKeyProvider` → `swarmauri_keyprovider_hierarchical.HierarchicalKeyProvider:HierarchicalKeyProvider`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_keyprovider_hierarchical` are `swarmauri-core`, `swarmauri-base`, `swarmauri-keyprovider-local`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/swarmauri_keyprovider_hierarchical/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_keyprovider_hierarchical` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_keyprovider_hierarchical`, use the source-declared public interfaces (`CreateRule`, `HierarchicalKeyProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_keyprovider_hierarchical` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_keyprovider_hierarchical`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/swarmauri_keyprovider_hierarchical/__init__.py). The `swarmauri_keyprovider_hierarchical` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_keyprovider_hierarchical` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_keyprovider_hierarchical` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/tests/test_functional.py)
- [tests/test_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/tests/test_perf.py)
- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/tests/test_readme_example.py)
- [tests/test_rfc7517.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/tests/test_rfc7517.py)
- [tests/test_rfc7518.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/tests/test_rfc7518.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_keyprovider_hierarchical` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/swarmauri_keyprovider_hierarchical/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_keyprovider_hierarchical` provides hierarchical key provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_keyprovider_hierarchical`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/swarmauri_keyprovider_hierarchical/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_keyprovider_hierarchical` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/swarmauri_keyprovider_hierarchical/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/pyproject.toml) provide the supporting context for `swarmauri_keyprovider_hierarchical`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_keyprovider_local](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_local/README.md): In-memory key provider for development and testing

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_keyprovider_hierarchical](https://pypi.org/project/swarmauri_keyprovider_hierarchical/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_keyprovider_hierarchical` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Routing policy**

`CreateRule` is a dataclass that narrows matching by any combination of
attributes:

- `provider` (required): the name of the child provider to route to.
- `klass`: limit matches to a specific `KeyClass` (symmetric or asymmetric).
- `algs`: iterable of allowed `KeyAlg` values.
- `uses`: iterable of desired `KeyUse` values; at least one requested use must
  intersect with the spec.
- `export_policies`: iterable of `ExportPolicy` values.

Rules are evaluated in order, and the first match wins. When an import policy
is not supplied, create rules are re-used for imports.

**Index persistence & discovery**

Pass `index_file` to persist the in-memory KID ? provider cache as JSON. On
startup, any known mappings are re-loaded (invalid provider names are skipped).
When a lookup is made for an unknown KID the provider probes each child with a
`get_key` call; if a child recognizes the KID the mapping is remembered and
future calls avoid probing. Destroying a key (without specifying a version)
removes the cached entry.

**Randomness & key derivation**

Use the `randomness_provider` and `derivation_provider` keyword arguments to
pin those helper methods to a specific child. If they are omitted the first
registered provider is used for both random bytes and HKDF requests.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_keyprovider_hierarchical` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_keyprovider_hierarchical` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_keyprovider_hierarchical` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_hierarchical/NOTICE) for attribution.
<!-- readme-standards:end notices -->

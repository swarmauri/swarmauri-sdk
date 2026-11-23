# MediaSigner

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>MediaSigner</strong></p>
<p align="center">Swarmauri signing facade plugin that aggregates registered SigningBase providers.</p>
<p align="center">
<a href="https://pypi.org/project/MediaSigner/"><img alt="pypi: MediaSigner" src="https://img.shields.io/pypi/v/MediaSigner?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/pyproject.toml"><img alt="Layer: plugins" src="https://img.shields.io/static/v1?label=Layer&amp;message=plugins&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/MediaSigner/"><img alt="Monthly PyPI downloads: MediaSigner" src="https://img.shields.io/pypi/dm/MediaSigner?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/README.md"><img alt="README hits: MediaSigner" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/60-plugins/media_signer/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

MediaSigner packages the asynchronous `Signer` facade that orchestrates registered
`SigningBase` providers. Moving the facade into a standalone plugin keeps the
core standards library lightweight while still enabling drop-in discovery of
specialised signers such as CMS, JWS, OpenPGP, PDF, and XMLDSig providers.

### Why This Package

* **Separation of concerns** ? standards remain focused on common abstractions
  while the plugin encapsulates optional dependencies.
* **Explicit opt-in** ? downstream projects can install only the signing stacks
  they need via the curated extras.
* **Consistent ergonomics** ? usage matches the historical
  `swarmauri_standard.signing.Signer` import, preserving existing tutorials and
  code samples.

### When to Use

Choose `MediaSigner` when your integration needs swarmauri signing facade plugin that aggregates registered SigningBase providers. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Unified signing faÃ§ade** ? talk to every installed `SigningBase` through a
  single async API that automatically discovers entry-point contributions.
- **Format-aware routing** ? delegates signing and verification to the provider
  registered for a format token such as `jws`, `pdf`, or `xmld`.
- **Optional plugin bundles** ? install curated extras (e.g. `[plugins]`) to
  bring in all available signer backends in one step.
- **Key-provider integration** ? share Swarmauri key providers with the facade
  so opaque key references resolve before signature creation.
- **Production-ready CLI** ? inspect capabilities, sign payloads, and verify
  results directly from the command line for fast automation.

### Non-Goals

`MediaSigner` owns swarmauri signing facade plugin that aggregates registered SigningBase providers. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-keyprovider-inmemory`, `cryptography`, `swarmauri-signing-cms`, `swarmauri-signing-jws`, `swarmauri-signing-openpgp`, `swarmauri-signing-pdf`, `swarmauri-signing-xmld`. Read the example’s inputs and service requirements before execution.

### Installation

**Using uv**

```bash
uv add MediaSigner

# install every optional backend
uv add "MediaSigner[plugins]"
```

The `[plugins]` extra pulls in CMS, JWS, OpenPGP, PDF, and XMLDSig signers.

**Using pip**

```bash
pip install MediaSigner

# with every optional backend
pip install "MediaSigner[plugins]"
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add MediaSigner
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install MediaSigner
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add MediaSigner
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/docs/readme/quick_start.py).

```python
import asyncio

from MediaSigner import MediaSigner
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider

# Optionally pass a key provider so plugins receive a shared source for
# retrieving signing material.
key_provider: IKeyProvider | None = None
signer = MediaSigner(key_provider=key_provider)


async def sign_payload(payload: bytes) -> None:
    signatures = await signer.sign_bytes("jws", key="my-key", payload=payload)
    assert signatures, "At least one signature should be returned"
    print(signer.supports("jws"))


asyncio.run(sign_payload(b"payload"))
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `MediaSigner` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/docs/readme/usage.py).

```python
import asyncio

from MediaSigner import MediaSigner
from swarmauri_core.key_providers.IKeyProvider import IKeyProvider

# Optionally pass a key provider so plugins receive a shared source for
# retrieving signing material.
key_provider: IKeyProvider | None = None
signer = MediaSigner(key_provider=key_provider)


async def sign_payload(payload: bytes) -> None:
    signatures = await signer.sign_bytes("jws", key="my-key", payload=payload)
    assert signatures, "At least one signature should be returned"
    print(signer.supports("jws"))


asyncio.run(sign_payload(b"payload"))
```
<!-- readme-standards:end example.usage -->

**Integrating a key provider**

Any Swarmauri key provider can be shared with the facade so backends receive
ready-to-use key material:

```python
import asyncio

from MediaSigner import MediaSigner
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider

provider = InMemoryKeyProvider(keys={"local://demo": b"secret"})
signer = MediaSigner(key_provider=provider)


async def main() -> None:
    signatures = await signer.sign_bytes(
        "jws",
        key="local://demo",
        payload=b"demo",
        alg="HS256",
        opts={"kid": "demo"},
    )
    print(signatures[0].mode)


asyncio.run(main())
```

**Discover installed plugins**

Use the facade to list installed signers and inspect their capabilities:

```python
for format_name in signer.supported_formats():
    capabilities = signer.supports(format_name)
    print(format_name, list(capabilities))
```

### Configuration

Configure `MediaSigner` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/MediaSigner/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `MediaSigner` source raises `SystemExit`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `MediaSigner` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `MediaSigner`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`MediaSigner` is located in `plugins` and owns swarmauri signing facade plugin that aggregates registered SigningBase providers. Source-declared APIs include `MediaSigner`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `MediaSigner`.

Source-declared exports or types: `MediaSigner`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/MediaSigner/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `console_scripts` → `media-signer` → `MediaSigner.cli:main`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `MediaSigner` are `swarmauri-core`, `swarmauri-base`, `swarmauri-keyprovider-inmemory`, `cryptography`, `swarmauri-signing-cms`, `swarmauri-signing-jws`, `swarmauri-signing-openpgp`, `swarmauri-signing-pdf`, `swarmauri-signing-xmld`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/MediaSigner/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `EmbeddedSigner`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `MediaSigner`, use the source-declared public interfaces (`MediaSigner`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `MediaSigner` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `MediaSigner`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/MediaSigner/__init__.py). The `MediaSigner` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `MediaSigner` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `MediaSigner` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_media_signer_cli.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/tests/test_media_signer_cli.py)
- [tests/test_media_signer_cms.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/tests/test_media_signer_cms.py)
- [tests/test_media_signer_jws.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/tests/test_media_signer_jws.py)
- [tests/test_media_signer_openpgp.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/tests/test_media_signer_openpgp.py)
- [tests/test_media_signer_pdf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/tests/test_media_signer_pdf.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `MediaSigner` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/MediaSigner/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `MediaSigner` provides swarmauri signing facade plugin that aggregates registered SigningBase providers; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `MediaSigner`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/MediaSigner/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `MediaSigner` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/MediaSigner/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/pyproject.toml) provide the supporting context for `MediaSigner`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_keyprovider_inmemory](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_keyprovider_inmemory/README.md): In-memory key provider for Swarmauri
- [swarmauri_signing_cms](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/README.md): CMS signer stub registered on the Swarmauri SigningBase registry
- [swarmauri_signing_jws](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/README.md): Composite JWS signer/verifier for Swarmauri
- [swarmauri_signing_openpgp](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_openpgp/README.md): OpenPGP signer stub registered on the Swarmauri SigningBase registry
- [swarmauri_signing_pdf](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_pdf/README.md): PDF signer built atop the Swarmauri CMS implementation
- [swarmauri_signing_xmld](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_xmld/README.md): XML Digital Signature implementation for the Swarmauri SigningBase registry

### Project Links

<!-- readme-standards:begin project-links -->
- [Changelog](https://github.com/swarmauri/swarmauri-sdk/releases)
- [Discussions](https://github.com/orgs/swarmauri/discussions)
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/60-plugins/media_signer#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Issues](https://github.com/swarmauri/swarmauri-sdk/issues)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/60-plugins/media_signer)
- [pypi: MediaSigner](https://pypi.org/project/MediaSigner/)
<!-- readme-standards:end project-links -->

- Source: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/60-plugins/media_signer>
- Documentation: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/60-plugins/media_signer#readme>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>
- Releases: <https://github.com/swarmauri/swarmauri-sdk/releases>
- Discussions: <https://github.com/orgs/swarmauri/discussions>

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `MediaSigner`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/60-plugins/media_signer` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Command line utility**

MediaSigner ships a small CLI for quick inspection and automation:

```bash
media-signer list                 # List available formats
media-signer supports jws         # Show capability metadata
media-signer sign-bytes jws \
  --alg HS256 \
  --key key.json \
  --input payload.bin \
  --output signatures.json

media-signer verify-bytes jws \
  --input payload.bin \
  --sigs signatures.json \
  --opts verify-keys.json
```

The CLI expects JSON files describing `KeyRef` objects and verification
materials matching the selected plugin.

---

## Governance

### Ownership and Decision Making

Changes to `MediaSigner` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`MediaSigner` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `MediaSigner` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/media_signer/NOTICE) for attribution.
<!-- readme-standards:end notices -->

# swarmauri_signing_dsse

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_signing_dsse</strong></p>
<p align="center">Composable DSSE envelope adapter that layers Pre-Authentication Encoding onto Swarmauri signing providers</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_dsse/"><img alt="pypi: swarmauri_signing_dsse" src="https://img.shields.io/pypi/v/swarmauri_signing_dsse?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_dsse/"><img alt="Monthly PyPI downloads: swarmauri_signing_dsse" src="https://img.shields.io/pypi/dm/swarmauri_signing_dsse?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/README.md"><img alt="README hits: swarmauri_signing_dsse" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_signing_dsse/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`DSSESigner` layers the [in-toto DSSE](https://github.com/secure-systems-lab/dsse) envelope format on top of any existing Swarmauri
signer. It computes the Pre-Authentication Encoding (PAE) defined by the spec, delegates raw signing and verification to the
wrapped provider, and exposes helpers for serializing envelopes in the DSSE JSON representation.

### Why This Package

`swarmauri_signing_dsse` isolates this responsibility: Composable DSSE envelope adapter that layers Pre-Authentication Encoding onto Swarmauri signing providers. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/swarmauri_signing_dsse/codec_json.py) exposes `DSSEEnvelope`, `DSSEJsonCodec`, `DSSESignatureRecord`, `DSSESigner`, `dsse_pae`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_signing_dsse` when your integration needs composable DSSE envelope adapter that layers Pre-Authentication Encoding onto Swarmauri signing providers. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Adds the `dsse-pae` canonicalization surface to any `SigningBase` provider.
- Supports detached signature workflows for bytes, digests, streams, and envelopes.
- Includes a strict JSON codec with typed helpers for building and inspecting DSSE envelopes.
- Maintains the inner signer's capability matrix while declaring DSSE-specific features (`detached_only`, `multi`).

### Non-Goals

`swarmauri_signing_dsse` owns composable DSSE envelope adapter that layers Pre-Authentication Encoding onto Swarmauri signing providers. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred Python packaging tool:

**Using uv**

```bash
uv add swarmauri_signing_dsse
```

**Using pip**

```bash
pip install swarmauri_signing_dsse
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_signing_dsse
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_signing_dsse
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_signing_dsse
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("swarmauri_signing_dsse")
assert package.__name__ == "swarmauri_signing_dsse"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri_signing_dsse`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("swarmauri_signing_dsse")
assert package.__name__ == "swarmauri_signing_dsse"
```
<!-- readme-standards:end example.usage -->

```python
import base64

from swarmauri_signing_dsse import DSSESigner, DSSEEnvelope
from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner

# Wrap an existing Swarmauri signer.
inner_signer = Ed25519EnvelopeSigner()
dsse_signer = DSSESigner(inner_signer)

# Prepare a DSSE envelope.
payload = b"example payload"
payload_b64 = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
envelope = DSSEEnvelope(payload_type="text/plain", payload_b64=payload_b64)

# Sign and verify using DSSE PAE over the payload.
key_ref = {"kind": "raw_ed25519_sk", "bytes": b"\x01" * 32}
signatures = await dsse_signer.sign_envelope(key_ref, envelope)
assert await dsse_signer.verify_envelope(envelope, signatures)
```

`DSSESigner` accepts existing DSSE JSON mappings or bytes anywhere an envelope is expected. The helper methods
`encode_envelope()` and `decode_envelope()` let you round-trip envelopes without reimplementing JSON handling.

### Configuration

Configure `swarmauri_signing_dsse` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/swarmauri_signing_dsse/codec_json.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_signing_dsse` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_signing_dsse` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `DSSEEnvelope`, `DSSEJsonCodec`, `DSSESignatureRecord`, `DSSESigner`, `dsse_pae`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_signing_dsse` is located in `community` and owns composable DSSE envelope adapter that layers Pre-Authentication Encoding onto Swarmauri signing providers. Source-declared APIs include `DSSEEnvelope`, `DSSEJsonCodec`, `DSSESignatureRecord`, `DSSESigner`, `dsse_pae`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_signing_dsse`.

Source-declared exports or types: `DSSEEnvelope`, `DSSEJsonCodec`, `DSSESignatureRecord`, `DSSESigner`, `dsse_pae`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/swarmauri_signing_dsse/codec_json.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.signings` → `dsse` → `swarmauri_signing_dsse:DSSESigner`
- `swarmauri.signings` → `DSSESigner` → `swarmauri_signing_dsse:DSSESigner`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_signing_dsse` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/swarmauri_signing_dsse/codec_json.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_signing_dsse` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_signing_dsse`, use the source-declared public interfaces (`DSSEEnvelope`, `DSSEJsonCodec`, `DSSESignatureRecord`, `DSSESigner`, `dsse_pae`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_signing_dsse` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_signing_dsse`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/swarmauri_signing_dsse/codec_json.py). The `swarmauri_signing_dsse` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_signing_dsse` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_signing_dsse` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_dsse_signer.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/tests/unit/test_dsse_signer.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_signing_dsse` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/swarmauri_signing_dsse/codec_json.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_signing_dsse` provides composable DSSE envelope adapter that layers Pre-Authentication Encoding onto Swarmauri signing providers; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_signing_dsse`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/swarmauri_signing_dsse/codec_json.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_signing_dsse` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/swarmauri_signing_dsse/codec_json.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/pyproject.toml) provide the supporting context for `swarmauri_signing_dsse`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/50-community/swarmauri_signing_dsse)
- [Repository](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_signing_dsse](https://pypi.org/project/swarmauri_signing_dsse/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_signing_dsse`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_signing_dsse` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_signing_dsse` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_signing_dsse` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_signing_dsse` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_signing_dsse` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the [Apache License 2.0](LICENSE).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_signing_dsse/NOTICE) for attribution.
<!-- readme-standards:end notices -->

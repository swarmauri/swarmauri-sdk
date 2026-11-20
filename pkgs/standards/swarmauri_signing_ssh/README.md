# swarmauri_signing_ssh

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_signing_ssh</strong></p>
<p align="center">OpenSSH-based signer for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_ssh/"><img alt="pypi: swarmauri_signing_ssh" src="https://img.shields.io/pypi/v/swarmauri_signing_ssh"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_ssh/"><img alt="Monthly PyPI downloads: swarmauri_signing_ssh" src="https://img.shields.io/pypi/dm/swarmauri_signing_ssh"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/README.md"><img alt="README hits: swarmauri_signing_ssh" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_signing_ssh/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

An OpenSSH-based signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

Features:
- Detached signatures powered by OpenSSH `ssh-keygen -Y` for Ed25519, RSA and
  ECDSA keys.
- Accepts private keys from filesystem paths or in-memory PEM blobs.
- JSON canonicalization built in with optional CBOR canonicalization via
  `cbor2`.
- Envelope helpers for canonicalized signing and verification workflows.

### Why This Package

`swarmauri_signing_ssh` isolates this responsibility: OpenSSH-based signer for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/swarmauri_signing_ssh/__init__.py) exposes `SshEnvelopeSigner`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_signing_ssh` when your integration needs openSSH-based signer for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `SshEnvelopeSigner`: Create and verify OpenSSH detached signatures.

### Non-Goals

`swarmauri_signing_ssh` owns openSSH-based signer for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- OpenSSH `ssh-keygen` (v8.2 or newer with `-Y` support) must be available on
  `PATH`.
- Install the optional `cbor` extra (`swarmauri_signing_ssh[cbor]`) to enable
  CBOR canonicalization.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_signing_ssh
```
<!-- readme-standards:end installation.uv -->

```bash
uv add swarmauri_signing_ssh
```

```bash
uv add "swarmauri_signing_ssh[cbor]"
```

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_signing_ssh
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_signing_ssh
```

Enable CBOR canonicalization when desired:

```bash
pip install "swarmauri_signing_ssh[cbor]"
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_signing_ssh
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_signing_ssh
```

```bash
poetry add swarmauri_signing_ssh -E cbor
```

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/docs/readme/quick_start.py).

```python
import asyncio
import subprocess
import tempfile
from pathlib import Path

from swarmauri_signing_ssh import SshEnvelopeSigner


async def main() -> bool:
    signer = SshEnvelopeSigner()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        priv_path = tmpdir_path / "id_ed25519"
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(priv_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        pubkey_line = (
            priv_path.with_suffix(".pub").read_text(encoding="utf-8").strip()
        )

        key = {
            "kind": "path",
            "priv": str(priv_path),
            "identity": "readme-demo",
        }
        payload = b"hello ssh signatures"

        signatures = await signer.sign_bytes(key, payload)
        return await signer.verify_bytes(
            payload,
            signatures,
            opts={"pubkeys": [pubkey_line], "identity": "readme-demo"},
        )


if __name__ == "__main__":  # pragma: no cover - README execution path
    print(asyncio.run(main()))
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_signing_ssh` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/docs/readme/usage.py).

```python
import asyncio
import subprocess
import tempfile
from pathlib import Path

from swarmauri_signing_ssh import SshEnvelopeSigner


async def main() -> bool:
    signer = SshEnvelopeSigner()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        priv_path = tmpdir_path / "id_ed25519"
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(priv_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        pubkey_line = (
            priv_path.with_suffix(".pub").read_text(encoding="utf-8").strip()
        )

        key = {
            "kind": "path",
            "priv": str(priv_path),
            "identity": "readme-demo",
        }
        payload = b"hello ssh signatures"

        signatures = await signer.sign_bytes(key, payload)
        return await signer.verify_bytes(
            payload,
            signatures,
            opts={"pubkeys": [pubkey_line], "identity": "readme-demo"},
        )


if __name__ == "__main__":  # pragma: no cover - README execution path
    print(asyncio.run(main()))
```
<!-- readme-standards:end example.usage -->

**Supported key references**

Provide the signer with a `KeyRef` dictionary:

- `{"kind": "path", "priv": "/path/to/id_ed25519", "identity": "optional"}`
  references a private key on disk.
- `{"kind": "pem", "priv": "-----BEGIN OPENSSH PRIVATE KEY-----..."}`
  accepts an OpenSSH private key as text/bytes. The key material is written to a
  secure temporary file for signing.

The signer derives the corresponding public key line, fingerprint (`kid`) and
algorithm token automatically.

**Verification options**

- Pass one or more OpenSSH public key lines via `opts["pubkeys"]` when calling
  `verify_bytes` or `verify_envelope`. Verification fails immediately when the
  list is missing or empty.
- Override the namespace used by `ssh-keygen -Y` through `opts["namespace"]`
  (defaults to `"file"`).
- Supply the expected signer identity with `opts["identity"]`. Identities
  default to `signer{i}` based on index order.
- Restrict acceptable signatures via the `require` mapping. Supported keys are
  `"algs"`, `"kids"` and `"min_signers"`.

**README example: sign and verify an SSH signature**


Running the script prints `True` once verification succeeds.

**Envelope workflows**

Use `sign_envelope` / `verify_envelope` alongside `canonicalize_envelope` to
operate on structured payloads. JSON canonicalization is always available;
enable the `cbor` extra to emit canonical CBOR bytes.

RSA keys default to `sha256` hashing but accept `hashalg="sha512"` via either
the key reference or `opts`. All signatures are detached (`features` include
`"detached_only"`), and multiple signatures can be verified in a single call.

### Configuration

Configure `swarmauri_signing_ssh` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/swarmauri_signing_ssh/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_signing_ssh` source raises `FileNotFoundError`, `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_signing_ssh` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SshEnvelopeSigner`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_signing_ssh` is located in `standards` and owns openSSH-based signer for Swarmauri. Source-declared APIs include `SshEnvelopeSigner`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_signing_ssh`.

Source-declared exports or types: `SshEnvelopeSigner`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/swarmauri_signing_ssh/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.signings` → `ssh` → `swarmauri_signing_ssh:SshEnvelopeSigner`
- `swarmauri.signings` → `SshEnvelopeSigner` → `swarmauri_signing_ssh:SshEnvelopeSigner`
<!-- readme-standards:end entry-points -->

The signer registers under the `swarmauri.signings` entry point as
`SshEnvelopeSigner`.

### Injected Dependencies

The direct installation dependencies of `swarmauri_signing_ssh` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/swarmauri_signing_ssh/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_signing_ssh` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_signing_ssh`, use the source-declared public interfaces (`SshEnvelopeSigner`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_signing_ssh` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_signing_ssh`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/swarmauri_signing_ssh/__init__.py). The `swarmauri_signing_ssh` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_signing_ssh` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_signing_ssh` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/tests/example/test_readme_example.py)
- [tests/functional/test_signer_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/tests/functional/test_signer_functional.py)
- [tests/perf/test_signer_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/tests/perf/test_signer_perf.py)
- [tests/unit/test_signer_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/tests/unit/test_signer_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_signing_ssh` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/swarmauri_signing_ssh/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_signing_ssh` provides openSSH-based signer for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_signing_ssh`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/swarmauri_signing_ssh/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_signing_ssh` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/swarmauri_signing_ssh/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/pyproject.toml) provide the supporting context for `swarmauri_signing_ssh`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/standards/swarmauri_signing_ssh#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/standards/swarmauri_signing_ssh)
- [pypi: swarmauri_signing_ssh](https://pypi.org/project/swarmauri_signing_ssh/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_signing_ssh` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_signing_ssh` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_signing_ssh` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_signing_ssh` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_signing_ssh` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_signing_ssh/NOTICE) for attribution.
<!-- readme-standards:end notices -->

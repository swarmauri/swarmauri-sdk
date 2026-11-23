# swarmauri_crypto_rust

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_crypto_rust</strong></p>
<p align="center">Rust-backed crypto provider for Swarmauri using Maturin</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_rust/"><img alt="pypi: swarmauri_crypto_rust" src="https://img.shields.io/pypi/v/swarmauri_crypto_rust"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_crypto_rust/"><img alt="Monthly PyPI downloads: swarmauri_crypto_rust" src="https://img.shields.io/pypi/dm/swarmauri_crypto_rust"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/README.md"><img alt="README hits: swarmauri_crypto_rust" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_crypto_rust/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_crypto_rust`: Rust-backed crypto provider for Swarmauri using Maturin

### Why This Package

`swarmauri_crypto_rust` isolates this responsibility: Rust-backed crypto provider for Swarmauri using Maturin. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml) exposes the checkout commands documented in Quick Start, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_crypto_rust` when your integration needs rust-backed crypto provider for Swarmauri using Maturin. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Rust-powered AEAD:** ChaCha20-Poly1305 encrypt/decrypt is implemented in Rust via the `ring` crate.
- **Memory safety:** Rust's memory safety guarantees prevent common crypto vulnerabilities.
- **Utility primitives:** Helper methods wrap keys and build multi-recipient envelopes on top of the AEAD primitive.
- **Self-contained:** No external C library dependencies are required.
- **Python integration:** Seamless integration with existing Python crypto workflows.

### Non-Goals

`swarmauri_crypto_rust` owns rust-backed crypto provider for Swarmauri using Maturin. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Building this package from source also requires Rust and Cargo through its declared Maturin backend. A compatible prebuilt wheel avoids the local Rust compilation step.

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Use the source-checkout workflow for this workspace or test harness.

### Installation

Pre-built wheels are published for common platforms. The Python facade requires the compiled Rust extension -- if the wheel
cannot be loaded the import will raise an `ImportError`, so be sure to install from PyPI or build the project locally before
using `RustCrypto`.

**Building from Source**

Requirements:

- Rust (1.70+)
- Python (3.10+)
- Maturin

```bash
# Install maturin
pip install maturin

# Build and install in development mode
maturin develop

# Or build a wheel
maturin build --release
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_crypto_rust
```
<!-- readme-standards:end installation.uv -->

If you manage dependencies with [uv](https://docs.astral.sh/uv/), add the package to your project manifest:

```bash
uv add swarmauri_crypto_rust
```

For ad-hoc usage you can also install directly into the current environment:

```bash
uv pip install swarmauri_crypto_rust
```

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_crypto_rust
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_crypto_rust
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_crypto_rust
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_crypto_rust
```

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/docs/readme/quick_start.py).

```python
from swarmauri_crypto_rust import RustCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
import asyncio


async def main():
    crypto = RustCrypto()

    # Create a symmetric key
    sym_key = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=crypto.generate_key(32),  # 32-byte key
    )

    # Encrypt and decrypt
    plaintext = b"Hello, Rust crypto world!"
    ciphertext = await crypto.encrypt(sym_key, plaintext)
    decrypted = await crypto.decrypt(sym_key, ciphertext)

    print(f"Original:  {plaintext}")
    print(f"Decrypted: {decrypted}")
    print(f"Match:     {plaintext == decrypted}")

    # Get version information
    version_info = crypto.get_version_info()
    print(f"Backend:   {version_info['backend']}")
    print(f"Version:   {version_info['rust_crypto_version']}")


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_crypto_rust` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/docs/readme/usage.py).

```python
from swarmauri_crypto_rust import RustCrypto
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
import asyncio


async def main():
    crypto = RustCrypto()

    # Create a symmetric key
    sym_key = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=crypto.generate_key(32),  # 32-byte key
    )

    # Encrypt and decrypt
    plaintext = b"Hello, Rust crypto world!"
    ciphertext = await crypto.encrypt(sym_key, plaintext)
    decrypted = await crypto.decrypt(sym_key, ciphertext)

    print(f"Original:  {plaintext}")
    print(f"Decrypted: {decrypted}")
    print(f"Match:     {plaintext == decrypted}")

    # Get version information
    version_info = crypto.get_version_info()
    print(f"Backend:   {version_info['backend']}")
    print(f"Version:   {version_info['rust_crypto_version']}")


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

The provider implements the asynchronous `ICrypto` contract, so you can await the core operations directly from Python. The
example below generates a symmetric key, performs an encrypt/decrypt round-trip, and inspects the version metadata published by
the Rust backend:

### Configuration

Configure `swarmauri_crypto_rust` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_crypto_rust` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml).

### Best Practices

Use the explicit `swarmauri_crypto_rust` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing the checkout commands documented in Quick Start; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_crypto_rust` is located in `standards` and owns rust-backed crypto provider for Swarmauri using Maturin. Source-declared APIs include the checkout commands documented in Quick Start. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

`swarmauri_crypto_rust` is a source-checkout harness. No installable Python namespace was found in the package layout; use its documented commands and test files.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.cryptos` → `rust` → `swarmauri_crypto_rust:RustCrypto`
- `swarmauri.cryptos` → `RustCrypto` → `swarmauri_crypto_rust:RustCrypto`
<!-- readme-standards:end entry-points -->

The provider is registered under multiple entry-points:

- `swarmauri.cryptos`: `RustCrypto`
- `peagen.plugins.cryptos`: `rust`

### Injected Dependencies

The direct installation dependencies of `swarmauri_crypto_rust` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_crypto_rust` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_crypto_rust`, use the source-declared public interfaces (the checkout commands documented in Quick Start) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_crypto_rust` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_crypto_rust`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml). The `swarmauri_crypto_rust` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_crypto_rust` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_crypto_rust` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/tests/test_readme_example.py)
- [tests/unit/test_RustCrypto.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/tests/unit/test_RustCrypto.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

```bash
# Run the full test suite from the package root
uv run --directory . --package swarmauri_crypto_rust pytest -v

# Execute only example-backed documentation tests
uv run --directory . --package swarmauri_crypto_rust pytest -m example -v
```

### Certification Status

No external certification is asserted for `swarmauri_crypto_rust` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_crypto_rust` provides rust-backed crypto provider for Swarmauri using Maturin; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_crypto_rust`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_crypto_rust` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml) provide the supporting context for `swarmauri_crypto_rust`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_crypto_rust](https://pypi.org/project/swarmauri_crypto_rust/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Contributions are welcome! Please see [CONTRIBUTING.md](../../../CONTRIBUTING.md) for guidelines.

### Development Setup

**Building**

```bash
# Development build
maturin develop

# Release build
maturin build --release

# Build with specific Python version
maturin build --interpreter python3.11
```

### Notes for Maintainers

**Swarmauri Crypto Rust**

High-performance Rust-backed crypto provider implementing the `ICrypto` contract via `CryptoBase` using the [ring](https://github.com/briansmith/ring) cryptography library.

- **ChaCha20-Poly1305** authenticated encryption exposed through the async Swarmauri crypto interface
- **Key wrapping helpers** that demonstrate envelope creation for multiple recipients
- **Sealed payload helpers** that reuse the AEAD primitive for simple sender-to-recipient encryption flows
- **Native Rust performance** for the core symmetric operations with Python ergonomics provided via Maturin/PyO3

**Algorithms Supported**

| Operation            | Algorithm         | Description                                                      |
| -------------------- | ----------------- | ---------------------------------------------------------------- |
| Symmetric Encryption | ChaCha20-Poly1305 | AEAD cipher with 256-bit keys implemented in Rust via `ring`     |
| Key Wrapping         | ECDH-ES+A256KW    | Demonstration helper that pads the DEK instead of performing ECDH |
| Sealed Boxes         | X25519-SEAL       | Simplified helper that serialises AEAD output for recipients      |

> **Note:** The wrapping, unwrapping, sealing, and multi-recipient helpers are intentionally simple demonstrations. They reuse
> the ChaCha20-Poly1305 primitive and do not implement authenticated X25519 key exchange. Treat them as examples rather than
> production-grade cryptography.

**Performance**

The AEAD primitive is executed inside compiled Rust code, so ChaCha20-Poly1305 operations benefit from the optimisations that
`ring` provides:

- **Native Speed**: Compiled Rust code runs at near C-level performance
- **Memory Efficiency**: The PyO3 bindings avoid unnecessary copies for common workloads
- **CPU Optimisation**: `ring` enables SIMD and hardware acceleration where available

The helper methods (`wrap`, `unwrap`, `seal`, and `encrypt_for_many`) are intentionally lightweight Python demonstrations and
do not provide additional performance characteristics beyond what the AEAD primitive already offers.

**Architecture**

```text
Python Layer
  RustCrypto (bridge) ----> swarmauri_core (types)
              |
              v
Rust Layer
  PyO3 bindings ---------> ring crypto backend
```

**Security**

- Uses the **ring** cryptography library, which is:

  - Maintained by security experts
  - Used in production by major tech companies
  - Focused on avoiding vulnerable patterns
  - Regularly audited for security issues

- **Memory Safety**: Rust prevents buffer overflows, use-after-free, and other memory corruption vulnerabilities common in C crypto libraries

- **Side-Channel Resistance**: The `ring` library implements constant-time operations to prevent timing attacks

> Warning: The helper methods for wrapping, sealing, and envelope creation are illustrative and intentionally omit a full X25519 key
> agreement. Do not rely on them for production key exchange without hardening the implementation.

**v0.1.0**

- Initial release with ChaCha20-Poly1305 AEAD
- Basic X25519 key agreement (simplified)
- Multi-recipient envelope support
- Maturin build system integration
- Comprehensive test suite

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_crypto_rust` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_crypto_rust` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_crypto_rust` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0 - See [LICENSE](LICENSE) for details.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_crypto_rust/NOTICE) for attribution.
<!-- readme-standards:end notices -->

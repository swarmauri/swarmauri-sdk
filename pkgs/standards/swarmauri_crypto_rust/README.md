![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_crypto_rust/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_crypto_rust" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_rust/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_crypto_rust.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_rust/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_crypto_rust" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_rust/">
        <img src="https://img.shields.io/pypi/l/swarmauri_crypto_rust" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_crypto_rust/">
        <img src="https://img.shields.io/pypi/v/swarmauri_crypto_rust?label=swarmauri_crypto_rust&color=green" alt="PyPI - swarmauri_crypto_rust"/></a>
</p>

---

## Swarmauri Crypto Rust

High-performance Rust-backed crypto provider implementing the `ICrypto` contract via `CryptoBase` using the [ring](https://github.com/briansmith/ring) cryptography library.

- **ChaCha20-Poly1305** authenticated encryption exposed through the async Swarmauri crypto interface
- **Key wrapping helpers** that demonstrate envelope creation for multiple recipients
- **Sealed payload helpers** that reuse the AEAD primitive for simple sender-to-recipient encryption flows
- **Native Rust performance** for the core symmetric operations with Python ergonomics provided via Maturin/PyO3

## Features

✨ **Rust-powered AEAD**: ChaCha20-Poly1305 encrypt/decrypt is implemented in Rust via the `ring` crate
🔒 **Memory Safe**: Rust's memory safety guarantees prevent common crypto vulnerabilities
🧰 **Utility Primitives**: Helper methods wrap keys and build multi-recipient envelopes on top of the AEAD primitive
📦 **Self-Contained**: No external C library dependencies are required
🐍 **Python Integration**: Seamless integration with existing Python crypto workflows

## Installation

Pre-built wheels are published for common platforms. The Python facade requires the compiled Rust extension – if the wheel
cannot be loaded the import will raise an `ImportError`, so be sure to install from PyPI or build the project locally before
using `RustCrypto`.

### pip

```bash
pip install swarmauri_crypto_rust
```

### Poetry

```bash
poetry add swarmauri_crypto_rust
```

### uv

If you manage dependencies with [uv](https://docs.astral.sh/uv/), add the package to your project manifest:

```bash
uv add swarmauri_crypto_rust
```

For ad-hoc usage you can also install directly into the current environment:

```bash
uv pip install swarmauri_crypto_rust
```

### Building from Source

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

## Usage

The provider implements the asynchronous `ICrypto` contract, so you can await the core operations directly from Python. The
example below generates a symmetric key, performs an encrypt/decrypt round-trip, and inspects the version metadata published by
the Rust backend:

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

## Algorithms Supported

| Operation            | Algorithm         | Description                                                      |
| -------------------- | ----------------- | ---------------------------------------------------------------- |
| Symmetric Encryption | ChaCha20-Poly1305 | AEAD cipher with 256-bit keys implemented in Rust via `ring`     |
| Key Wrapping         | ECDH-ES+A256KW    | Demonstration helper that pads the DEK instead of performing ECDH |
| Sealed Boxes         | X25519-SEAL       | Simplified helper that serialises AEAD output for recipients      |

> **Note:** The wrapping, unwrapping, sealing, and multi-recipient helpers are intentionally simple demonstrations. They reuse
> the ChaCha20-Poly1305 primitive and do not implement authenticated X25519 key exchange. Treat them as examples rather than
> production-grade cryptography.

## Performance

The AEAD primitive is executed inside compiled Rust code, so ChaCha20-Poly1305 operations benefit from the optimisations that
`ring` provides:

- **Native Speed**: Compiled Rust code runs at near C-level performance
- **Memory Efficiency**: The PyO3 bindings avoid unnecessary copies for common workloads
- **CPU Optimisation**: `ring` enables SIMD and hardware acceleration where available

The helper methods (`wrap`, `unwrap`, `seal`, and `encrypt_for_many`) are intentionally lightweight Python demonstrations and
do not provide additional performance characteristics beyond what the AEAD primitive already offers.

## Architecture

```
┌─────────────────────────────────────────────┐
│              Python Layer                   │
│  ┌─────────────────┐  ┌─────────────────┐   │
│  │   RustCrypto    │  │  swarmauri_core │   │
│  │    (Bridge)     │  │    (Types)      │   │
│  └─────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────┘
                       │
┌─────────────────────────────────────────────┐
│               Rust Layer                    │
│  ┌─────────────────┐  ┌─────────────────┐   │
│  │   PyO3 Bindings │  │   ring crypto   │   │
│  │   (Interface)   │  │   (Backend)     │   │
│  └─────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────┘
```

## Security

- Uses the **ring** cryptography library, which is:

  - Maintained by security experts
  - Used in production by major tech companies
  - Focused on avoiding vulnerable patterns
  - Regularly audited for security issues

- **Memory Safety**: Rust prevents buffer overflows, use-after-free, and other memory corruption vulnerabilities common in C crypto libraries

- **Side-Channel Resistance**: The `ring` library implements constant-time operations to prevent timing attacks

> ⚠️ The helper methods for wrapping, sealing, and envelope creation are illustrative and intentionally omit a full X25519 key
> agreement. Do not rely on them for production key exchange without hardening the implementation.

## Development

### Testing

```bash
# Run the full test suite from the package root
uv run --directory . --package swarmauri_crypto_rust pytest -v

# Execute only example-backed documentation tests
uv run --directory . --package swarmauri_crypto_rust pytest -m example -v
```

### Building

```bash
# Development build
maturin develop

# Release build
maturin build --release

# Build with specific Python version
maturin build --interpreter python3.11
```

## Entry Points

The provider is registered under multiple entry-points:

- `swarmauri.cryptos`: `RustCrypto`
- `peagen.plugins.cryptos`: `rust`

## License

Apache-2.0 - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../../../CONTRIBUTING.md) for guidelines.

## Changelog

### v0.1.0

- Initial release with ChaCha20-Poly1305 AEAD
- Basic X25519 key agreement (simplified)
- Multi-recipient envelope support
- Maturin build system integration
- Comprehensive test suite

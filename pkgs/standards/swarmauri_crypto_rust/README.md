![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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

- **ChaCha20-Poly1305** symmetric encrypt/decrypt (AEAD)
- **X25519** key agreement and sealed boxes (simplified implementation)
- **Multi-recipient envelopes** using ChaCha20-Poly1305 + ECDH key wrapping
- **Native Rust performance** with Python convenience via Maturin/PyO3

## Features

✨ **High Performance**: Native Rust implementation using the battle-tested `ring` crate  
🔒 **Memory Safe**: Rust's memory safety guarantees prevent common crypto vulnerabilities  
🚀 **Zero-Copy Operations**: Efficient data handling between Python and Rust  
🎯 **Modern Algorithms**: ChaCha20-Poly1305 AEAD and X25519 elliptic curves  
📦 **Self-Contained**: No external C library dependencies  
🐍 **Python Integration**: Seamless integration with existing Python crypto workflows

## Installation

```bash
pip install swarmauri_crypto_rust
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

| Operation            | Algorithm         | Description                     |
| -------------------- | ----------------- | ------------------------------- |
| Symmetric Encryption | ChaCha20-Poly1305 | AEAD cipher with 256-bit keys   |
| Key Wrapping         | ECDH-ES+A256KW    | Simplified ECDH key agreement   |
| Sealed Boxes         | X25519-SEAL       | Anonymous public key encryption |

## Performance

The Rust implementation provides significant performance benefits:

- **Native Speed**: Compiled Rust code runs at near C-level performance
- **Memory Efficiency**: Zero-copy operations where possible
- **CPU Optimization**: SIMD and hardware acceleration via `ring`
- **Parallel Processing**: Rust's fearless concurrency for batch operations

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

## Development

### Testing

```bash
# Run tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=swarmauri_crypto_rust

# Benchmark tests
python -m pytest tests/ -m perf
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

![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_suite_yubikey/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_cipher_suite_yubikey" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_yubikey/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_yubikey.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_yubikey/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_suite_yubikey" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_yubikey/">
        <img src="https://img.shields.io/pypi/l/swarmauri_cipher_suite_yubikey" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_yubikey/">
        <img src="https://img.shields.io/pypi/v/swarmauri_cipher_suite_yubikey?label=swarmauri_cipher_suite_yubikey&color=green" alt="PyPI - swarmauri_cipher_suite_yubikey"/></a>
</p>

---

# Swarmauri Cipher Suites YubiKey

`YubiKeyCipherSuite` models a conservative YubiKey configuration that focuses on
PIV-backed signing and key transport. It exposes the algorithms commonly
available on non-FIPS YubiKey models without promising token-side bulk
encryption.

## Features

- Normalizes YubiKey signing (`sign`/`verify`) and key wrap (`wrap`/`unwrap`)
  operations.
- Provides policy defaults for RSA-PSS and ECDSA, including default hash
  coupling and salt lengths.
- Surfaces dialect metadata so crypto providers can route requests to the PIV
  driver (`piv:<alg>`), including optional slot tagging.
- Documents token policy (allowed curves, hash functions, attestation
  expectations) in a single place.

## Installation

### pip

```bash
pip install swarmauri_cipher_suite_yubikey
```

### uv (dependency)

```bash
uv add swarmauri_cipher_suite_yubikey
```

### uv (environment)

```bash
uv pip install swarmauri_cipher_suite_yubikey
```

## Usage

### 1. Instantiate the suite

```python
from swarmauri_cipher_suite_yubikey import YubiKeyCipherSuite

suite = YubiKeyCipherSuite(name="piv-default")
```

The suite accepts a friendly name so you can register multiple policy variants
if you run different tokens.

### 2. Normalize a signing request

```python
from swarmauri_core.cipher_suites.types import KeyRef

key = KeyRef(kid="sig-slot-9c", slot="9c")
descriptor = suite.normalize(op="sign", alg="ES256", key=key)

print(descriptor["mapped"]["provider"])  # -> "piv:ES256:slot=9c"
print(descriptor["params"]["hash"])       # -> "SHA256" (defaulted)
```

`normalize` returns a dictionary with the canonical algorithm, provider
identifier, defaulted parameter set, and suite policy. Crypto providers can
forward these values directly to the PIV driver without re-implementing
YubiKey-specific logic.

### 3. Wrap a key for transport

```python
transport_descriptor = suite.normalize(op="wrap")
print(transport_descriptor["mapped"]["provider"])  # -> "piv:RSA-OAEP-256"
print(transport_descriptor["params"])              # -> {"mgf1Hash": "SHA256"}
```

When no algorithm is supplied, the suite picks sensible defaults (`ES256` for
signing, `RSA-OAEP-256` for key wrap) while still respecting the policy limits.

### 4. Inspect supported algorithms and features

```python
for op, algs in suite.supports().items():
    print(op, sorted(algs))

print(suite.features()["notes"][0])
```

These helpers allow orchestration layers to discover the token capabilities,
render documentation, or validate client requests before invoking the hardware.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`YubiKeyCipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

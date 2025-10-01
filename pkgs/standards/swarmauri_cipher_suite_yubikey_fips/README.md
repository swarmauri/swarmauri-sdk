![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_cipher_suite_yubikey_fips/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_cipher_suite_yubikey_fips" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_yubikey_fips/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_cipher_suite_yubikey_fips.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_yubikey_fips/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_cipher_suite_yubikey_fips" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_yubikey_fips/">
        <img src="https://img.shields.io/pypi/l/swarmauri_cipher_suite_yubikey_fips" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_cipher_suite_yubikey_fips/">
        <img src="https://img.shields.io/pypi/v/swarmauri_cipher_suite_yubikey_fips?label=swarmauri_cipher_suite_yubikey_fips&color=green" alt="PyPI - swarmauri_cipher_suite_yubikey_fips"/></a>
</p>

---

# Swarmauri Cipher Suites YubiKey FIPS

`YubiKeyFipsCipherSuite` captures the subset of YubiKey functionality that is
available on FIPS Series tokens. It excludes EdDSA, tightens hash policy, and
requires slot attestation, making it a drop-in choice for regulated
environments.

## Features

- Limits signing algorithms to FIPS-approved RSA-PSS and NIST P-256/P-384 ECDSA.
- Encodes the requirement for attestation before use so orchestrators can gate
  slots appropriately.
- Supplies parameter defaults for RSA-PSS (salt length, MGF1 hash) and ECDSA
  hashing to avoid mismatched requests.
- Documents the FIPS policy posture and exposes a provider identifier for the
  PIV-backed mechanisms (`piv:<alg>`).

## Installation

### pip

```bash
pip install swarmauri_cipher_suite_yubikey_fips
```

### uv (dependency)

```bash
uv add swarmauri_cipher_suite_yubikey_fips
```

### uv (environment)

```bash
uv pip install swarmauri_cipher_suite_yubikey_fips
```

## Usage

### 1. Instantiate the suite with a descriptive name

```python
from swarmauri_cipher_suite_yubikey_fips import YubiKeyFipsCipherSuite

suite = YubiKeyFipsCipherSuite(name="piv-fips")
```

### 2. Normalize a FIPS-compliant signing request

```python
from swarmauri_core.cipher_suites.types import KeyRef

key = KeyRef(kid="fips-slot-9a", slot="9a")
descriptor = suite.normalize(op="sign", alg="PS256", key=key)

print(descriptor["mapped"]["provider"])  # -> "piv:PS256:slot=9a"
print(descriptor["params"]["saltLen"])    # -> 32 (hash length default)
```

All responses include the policy metadata, making it easy to enforce controls
(such as requiring attestation) at runtime.

### 3. Route wrap/unwrap requests

```python
wrap_descriptor = suite.normalize(op="wrap")
unwrap_descriptor = suite.normalize(op="unwrap", alg="RSA-OAEP-256")

for d in (wrap_descriptor, unwrap_descriptor):
    assert d["mapped"]["provider"].startswith("piv:RSA-OAEP-256")
```

The suite guarantees that both wrap and unwrap operations stay aligned with the
RSA-OAEP-256 configuration expected by PIV.

### 4. Discover compliance metadata

```python
features = suite.features()
print(features["compliance"]["fips"])      # -> True
print(features["constraints"]["hashes"])   # -> ["SHA256", "SHA384"]
```

Use the feature description to document service capabilities or reject
non-compliant requests before they hit hardware.

## Entry Point

The suite registers under the `swarmauri.cipher_suites` entry point as
`YubiKeyFipsCipherSuite`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

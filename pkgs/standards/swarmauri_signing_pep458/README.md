![Swarmauri Brand Theme](https://github.com/swarmauri/swarmauri-sdk/blob/main/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_pep458/">
        <img src="https://img.shields.io/badge/status-planning-blueviolet" alt="Development status" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signing_pep458/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_pep458.svg" alt="Python versions" />
    </a>
    <a href="https://pypi.org/project/swarmauri_signing_pep458/">
        <img src="https://img.shields.io/badge/signature-format-tuf%2Fpep458-brightgreen" alt="Signature format" />
    </a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/standards/swarmauri_signing_pep458">
        <img src="https://img.shields.io/badge/cryptography-backed-FFD700" alt="cryptography dependency" />
    </a>
</p>

---

# swarmauri_signing_pep458

`swarmauri_signing_pep458` packages a detached signature provider that implements
[PEP 458](https://peps.python.org/pep-0458/) style signing for The Update Framework
(TUF) metadata. It brings canonical JSON, multi-algorithm support, and quorum-aware
verification to the Swarmauri runtime so supply-chain aware components can produce
and validate repository metadata with a uniform API.

## Key Features

- **PEP 458 compatible format** – Signatures emit the `tuf/pep458` envelope with
  `method`, `keyid`, and base64-encoded payloads so the metadata aligns with the
  specification's detached signature requirements.
- **Deterministic canonicalization** – Canonicalizes envelopes using TUF's
  lexicographically-sorted JSON encoding to guarantee byte-for-byte reproducibility.
- **Multiple signature algorithms** – Supports Ed25519 for online roles and
  RSA-PSS-SHA256 for offline root-style metadata, allowing you to mix schemes per
  role.
- **Quorum aware verification** – Enforces `min_signers`, explicit key-id allow
  lists, and algorithm restrictions during verification to help model offline
  threshold signing policies.
- **Flexible key inputs** – Accepts cryptography key objects, PEM encoded key
  material, or Swarmauri `KeyRef` dictionaries for both signing and verification.

## Installation

### Using `uv`

```bash
uv add swarmauri_signing_pep458
```

### Using `pip`

```bash
pip install swarmauri_signing_pep458
```

## Quick Start

```python
import asyncio
from cryptography.hazmat.primitives.asymmetric import ed25519
from swarmauri_signing_pep458 import Pep458Signer

async def main() -> None:
    signer = Pep458Signer()
    private = ed25519.Ed25519PrivateKey.generate()
    keyref = {"kind": "cryptography_obj", "obj": private, "alg": "Ed25519"}

    payload = b"release metadata"
    signatures = await signer.sign_bytes(keyref, payload)

    is_valid = await signer.verify_bytes(
        payload,
        signatures,
        opts={"pubkeys": [private.public_key()]},
    )
    print(f"Signature valid? {is_valid}")

asyncio.run(main())
```

## Signature Format

Each signature returned by the signer follows this shape:

```json
{
  "format": "tuf/pep458",
  "method": "ed25519",
  "alg": "Ed25519",
  "keyid": "base64(SHA256(method || SPKI))",
  "sig": "base64(signature-bytes)"
}
```

Use the `method` label when matching public keys and verifying thresholds for a
particular TUF role.

## Verification Policy Hints

The `verify_bytes` and `verify_envelope` APIs accept a `require` mapping with the
following helpful keys:

- `min_signers`: Require at least _n_ distinct key ids to validate.
- `algs`: Restrict verification to a subset of algorithms, e.g. `("Ed25519",)`. The
  values are normalized case-insensitively.
- `kids`: Whitelist key identifiers allowed to satisfy the policy.
- `pubkeys`: Explicit public key materials to use when verifying (PEM strings,
  cryptography objects, or `{"kind": "pem", "pub": ...}` dictionaries).

## Relationship to the Cipher Suite

Pair this package with `swarmauri_cipher_suite_pep458` to describe repository role
policies, canonicalization settings, and default algorithm choices across the
Swarmauri ecosystem.

## Development

- Format the code with `ruff format .` and lint with `ruff check . --fix`.
- Run the asynchronous unit tests with `pytest` once cryptography dependencies are
  available.
- Contributions should include updates to documentation fragments and policy tables
  when new capabilities are added.

## License

This project is licensed under the [Apache License 2.0](LICENSE).

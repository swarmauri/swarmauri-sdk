![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_dsse/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_dsse" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_dsse/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_dsse.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_dsse/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_dsse" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_dsse/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_dsse" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_dsse/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_dsse?label=swarmauri_signing_dsse&color=green" alt="PyPI - swarmauri_signing_dsse"/></a>
</p>

---

# Swarmauri Signing DSSE

`DSSESigner` layers the [in-toto DSSE](https://github.com/secure-systems-lab/dsse) envelope format on top of any existing Swarmauri
signer. It computes the Pre-Authentication Encoding (PAE) defined by the spec, delegates raw signing and verification to the
wrapped provider, and exposes helpers for serializing envelopes in the DSSE JSON representation.

## Features

- Adds the `dsse-pae` canonicalization surface to any `SigningBase` provider.
- Supports detached signature workflows for bytes, digests, streams, and envelopes.
- Includes a strict JSON codec with typed helpers for building and inspecting DSSE envelopes.
- Maintains the inner signer's capability matrix while declaring DSSE-specific features (`detached_only`, `multi`).

## Installation

Install the package with your preferred Python packaging tool:

### Using `uv`

```bash
uv add swarmauri_signing_dsse
```

### Using `pip`

```bash
pip install swarmauri_signing_dsse
```

## Usage

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

## License

This project is licensed under the [Apache License 2.0](LICENSE).

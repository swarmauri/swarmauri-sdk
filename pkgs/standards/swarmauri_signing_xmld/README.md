<p align="center">
  <img src="../../../assets/swarmauri.brand.theme.svg" alt="Swarmauri logotype" width="420" />
</p>

<h1 align="center">swarmauri_signing_xmld</h1>

<p align="center">
  <a href="https://img.shields.io/badge/status-experimental-ff6f61?style=for-the-badge"><img src="https://img.shields.io/badge/status-experimental-ff6f61?style=for-the-badge" alt="Status: experimental" /></a>
  <a href="https://img.shields.io/badge/license-Apache--2.0-0a6ebd?style=for-the-badge"><img src="https://img.shields.io/badge/license-Apache--2.0-0a6ebd?style=for-the-badge" alt="License: Apache-2.0" /></a>
  <a href="https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-4b8bbe?style=for-the-badge"><img src="https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-4b8bbe?style=for-the-badge" alt="Python versions" /></a>
</p>

`swarmauri_signing_xmld` packages an XML Digital Signature (`XMLDSig`) provider that registers
with the Swarmauri `SigningBase` registry. The signer focuses on canonicalized
XML payloads and produces detached signatures that can be embedded into
workflow-specific envelopes.

## Installation

### uv

```bash
uv pip install swarmauri_signing_xmld
```

### pip

```bash
pip install swarmauri_signing_xmld
```

## Usage

```python
from swarmauri_signing_xmld import XMLDSigner

signer = XMLDSigner()
xml_payload = """<note><to>Alice</to><from>Bob</from></note>""".encode()

signature = await signer.sign_bytes(
    key={
        "kind": "pem",
        "private_key": "/path/to/private_key.pem",
        "certificate": "/path/to/certificate.pem",
    },
    payload=xml_payload,
)
```

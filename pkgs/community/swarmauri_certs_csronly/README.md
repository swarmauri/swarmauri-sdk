# swarmauri_certs_csronly

A community-provided certificate service that builds PKCS#10 Certificate Signing Requests (CSRs).

## Features
- Generate CSRs using RSA, EC, and Ed25519 keys
- Support for subject alternative names and basic constraints

## Installation
```bash
pip install swarmauri_certs_csronly
```

## Usage
```python
from swarmauri_certs_csronly import CsrOnlyService

service = CsrOnlyService()
csr_bytes = await service.create_csr(key_ref, {"CN": "example"})
```

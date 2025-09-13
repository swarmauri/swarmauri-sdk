![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri Certs Local CA

A local certificate authority implementing the `ICertService` interface for issuing and verifying X.509 certificates. Useful for development and testing environments.

Features:
- CSR generation with subject alternative names
- Self-signed certificate issuance
- Signing CSRs to produce leaf certificates
- Basic certificate verification and parsing
- Optional IDNA support for internationalized DNS names

## Installation

```bash
pip install swarmauri_certs_local_ca
```

## Usage

Below is a minimal end‑to‑end example that issues and verifies a leaf
certificate signed by a local certificate authority.  The helper function
`_key` creates the ``KeyRef`` objects required by the service.

```python
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_certs_local_ca import LocalCaCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


def _key(name: str) -> KeyRef:
    sk = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = sk.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid=name,
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


async def main() -> None:
    svc = LocalCaCertService()
    ca_key = _key("ca")
    leaf_key = _key("leaf")

    # Create a certificate signing request for the leaf key.
    csr = await svc.create_csr(leaf_key, {"CN": "leaf"})

    # Sign the CSR with the CA key to produce a leaf certificate.
    cert = await svc.sign_cert(csr, ca_key, issuer={"CN": "ca"})

    # Verify the newly issued certificate.
    result = await svc.verify_cert(cert)
    print(result["valid"])  # True


asyncio.run(main())
```

## Entry Point

The service registers under the `swarmauri.cert_services` entry point as `LocalCaCertService`.

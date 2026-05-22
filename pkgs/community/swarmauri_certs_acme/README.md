![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_certs_acme/">
        <img src="https://static.pepy.tech/badge/swarmauri_certs_acme/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_acme/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_certs_acme.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_acme/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_acme/">
        <img src="https://img.shields.io/pypi/l/swarmauri_certs_acme" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_certs_acme/">
        <img src="https://img.shields.io/pypi/v/swarmauri_certs_acme?label=swarmauri_certs_acme&color=green" alt="PyPI - swarmauri_certs_acme"/></a>
</p>

# Swarmauri ACME Certificate Service

`swarmauri_certs_acme` provides `AcmeCertService`, a Swarmauri certificate service for ACME v2 certificate issuance. It uses the Python `acme` client and `cryptography` primitives to build PKCS#10 certificate signing requests, submit ACME orders, finalize issued certificates, return PEM or DER chains, and inspect X.509 certificate metadata.

## Why Swarmauri ACME Certificate Service?

Use this package when Swarmauri workloads need automated certificate issuance through an ACME certificate authority such as Let's Encrypt. It keeps ACME directory discovery, account-key handling, CSR creation, order finalization, certificate parsing, and capability reporting behind the common Swarmauri certificate-service interface.

## FAQ

### Q: What standards does this package target?

A: `AcmeCertService` targets ACME v2 from RFC 8555, PKCS#10 CSRs from RFC 2986, and X.509 certificate parsing semantics from RFC 5280.

### Q: Does this package solve ACME challenges?

A: No. DNS-01 or HTTP-01 challenge automation must be handled by the caller or surrounding infrastructure. This service focuses on CSR construction, ACME order submission/finalization, and certificate retrieval.

### Q: What key algorithms does it advertise?

A: `supports()` reports RSA-2048, RSA-3072, EC-P256, and EC-P384 key support with RS256, ES256, and ES384 signature algorithms.

### Q: When should I use another certificate package?

A: Use local or self-signed certificate packages for offline development and internal test chains. Use cloud, enterprise CA, or verification-specific packages when certificate issuance or validation is owned by another provider.

## Features

- `AcmeCertService` class registered under the `swarmauri.certs` entry point.
- ACME v2 directory discovery and `ClientV2` order finalization.
- PEM account-key loading from Swarmauri `KeyRef` objects.
- PKCS#10 CSR creation with common-name and DNS subject alternative name support.
- PEM full-chain retrieval by default, with DER chain output available.
- X.509 certificate parsing and basic validity-window inspection.
- Capability metadata for supported key algorithms, signature algorithms, profiles, and features.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- ACME account private key material available as PEM bytes.
- A CSR or host private key material for CSR creation.
- Network access to the target ACME directory.
- External automation for ACME challenge presentation and validation.
- Awareness of CA staging and production rate limits before running automated issuance.

## Installation

Install with `uv`:

```bash
uv add swarmauri_certs_acme
```

Install with `pip`:

```bash
pip install swarmauri_certs_acme
```

## Usage

Create an ACME service with a PEM account key:

```python
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef

account_key = KeyRef(material=Path("account-key.pem").read_bytes())
service = AcmeCertService(
    account_key=account_key,
    contact_emails=["admin@example.com"],
)

print(service.supports()["features"])
```

Build a CSR for a host key:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    account_key = KeyRef(material=Path("account-key.pem").read_bytes())
    host_key = KeyRef(material=Path("server-key.pem").read_bytes())
    service = AcmeCertService(account_key=account_key)

    csr = await service.create_csr(
        key=host_key,
        subject={"CN": "example.com"},
        san={"dns": ["example.com", "www.example.com"]},
    )
    Path("server.csr").write_bytes(csr)


asyncio.run(main())
```

Submit a CSR and persist the returned certificate chain:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    account_key = KeyRef(material=Path("account-key.pem").read_bytes())
    service = AcmeCertService(account_key=account_key)

    certificate_chain = await service.sign_cert(
        csr=Path("server.csr").read_bytes(),
        ca_key=account_key,
    )
    Path("server-fullchain.pem").write_bytes(certificate_chain)


asyncio.run(main())
```

Inspect an issued certificate:

```python
import asyncio
from pathlib import Path

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import KeyRef


async def main() -> None:
    account_key = KeyRef(material=Path("account-key.pem").read_bytes())
    service = AcmeCertService(account_key=account_key)
    pem_chain = Path("server-fullchain.pem").read_bytes()

    verification = await service.verify_cert(pem_chain)
    parsed = await service.parse_cert(pem_chain)

    print(verification["valid"])
    print(parsed["subject"])


asyncio.run(main())
```

## Related Packages

Certificate service packages:

- [swarmauri_certs_local_ca](https://pypi.org/project/swarmauri_certs_local_ca/)
- [swarmauri_certs_self_signed](https://pypi.org/project/swarmauri_certs_self_signed/)
- [swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
- [swarmauri_certs_azure](https://pypi.org/project/swarmauri_certs_azure/)
- [swarmauri_certs_cfssl](https://pypi.org/project/swarmauri_certs_cfssl/)
- [swarmauri_certservice_stepca](https://pypi.org/project/swarmauri_certservice_stepca/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines the certificate-service interfaces and `KeyRef` types.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `CertServiceBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides standard Swarmauri components used alongside certificate workflows.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Use ACME staging endpoints during development and load tests.
- Store account and host private keys in a secure KMS or vault-backed `KeyRef` workflow.
- Automate challenge presentation outside this package before finalizing orders.
- Cache issued certificate chains and renew before `not_after` to avoid service interruptions.

## License

Apache-2.0

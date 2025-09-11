# swarmauri_certs_ocspverify

OCSP-based certificate verification service for the Swarmauri SDK.

This package provides an implementation of an `ICertService` that checks
certificate revocation status using the Online Certificate Status Protocol
(OCSP) defined in [RFC 6960](https://www.rfc-editor.org/rfc/rfc6960) while
remaining compatible with X.509 certificate guidelines from
[RFC 5280](https://www.rfc-editor.org/rfc/rfc5280).

## Features
- Parse PEM certificates to extract subject, issuer and OCSP responder URLs.
- Verify certificate status via OCSP responders advertised in the certificate's
  Authority Information Access extension.

## Installation
```bash
pip install swarmauri_certs_ocspverify
```

## Usage
```python
from swarmauri_certs_ocspverify import OcspVerifyService

svc = OcspVerifyService()
# verify and parse certificates using svc.verify_cert(...) and svc.parse_cert(...)
```

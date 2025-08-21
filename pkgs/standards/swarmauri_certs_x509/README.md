# swarmauri_certs_x509

X.509 certificate service plugin for Swarmauri using the `cryptography` library.

## Features
- Create CSRs
- Issue self-signed certificates
- Sign certificates with a CA
- Verify certificate chains

## RFC References
- [RFC 2986](https://datatracker.ietf.org/doc/html/rfc2986) – PKCS #10 Certification Request Syntax
- [RFC 5280](https://datatracker.ietf.org/doc/html/rfc5280) – Internet X.509 Public Key Infrastructure Certificate and CRL Profile

## Testing
Run unit, performance, and functional tests with:

```bash
uv run --package swarmauri_certs_x509 --directory standards/swarmauri_certs_x509 pytest
```

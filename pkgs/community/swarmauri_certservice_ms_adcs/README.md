# swarmauri_certservice_ms_adcs

Community plugin providing a certificate service client for Microsoft Active Directory Certificate Services (AD CS).

## Features

- Build and sign PKCS#10 certificate signing requests (CSR) according to RFC 2986.
- Parse and verify X.509 certificates as defined in RFC 5280.
- Optional authentication helpers for NTLM and Kerberos.

## Installation

```bash
pip install swarmauri_certservice_ms_adcs[ntlm,kerberos]
```

## Usage

```python
from swarmauri_certservice_ms_adcs import MsAdcsCertService, _AuthCfg

svc = MsAdcsCertService(base_url="https://adcs.example.com/certsrv",
                        auth=_AuthCfg(mode="none"))
```

![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Remote CA Cert Service

A certificate enrollment bridge implementing the `ICertService` interface and
forwarding CSRs to a remote Certificate Authority.

Features:
- Posts CSRs to a remote endpoint and returns issued certificates.
- Minimal parsing helpers for certificate snippets.
- Designed around X.509 as defined in RFC 5280 and Enrollment over Secure
  Transport (EST) in RFC 7030.

## Installation

```bash
pip install swarmauri_certs_remote_ca
```

## Entry Point

The service registers under the `swarmauri.certs` entry point as
`RemoteCaCertService`.

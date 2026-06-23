![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_transport_https_unicast/">
        <img src="https://static.pepy.tech/badge/swarmauri_transport_https_unicast/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_https_unicast/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_https_unicast.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_https_unicast/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_https_unicast/">
        <img src="https://img.shields.io/pypi/l/swarmauri_transport_https_unicast" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_transport_https_unicast/">
        <img src="https://img.shields.io/pypi/v/swarmauri_transport_https_unicast?label=swarmauri_transport_https_unicast&color=green" alt="PyPI - swarmauri_transport_https_unicast"/></a>
</p>

# swarmauri_transport_https_unicast

`swarmauri_transport_https_unicast` provides a policy-bound HTTPS client
transport that composes HTTPX with Swarmauri TLS 1.3 cipher policy, X.509
certificate verification, HTTP signature headers, bearer-token forwarding, and
JWS body signing or verification.

## Features

- Advertises HTTPS-over-TLS unicast transport capabilities through
  `TransportBase`.
- Uses HTTPX for concrete HTTPS request dispatch.
- Applies bearer tokens, `HttpSigMiddleware`-compatible HMAC headers, and JWS
  request-body signatures.
- Verifies response-body JWS payloads before returning transport results.
- Exposes X.509 preflight verification through `X509VerifyService`.
- Publishes TLS 1.3 cipher-suite policy metadata through `Tls13CipherSuite`.

## Installation

With `uv`:

```bash
uv add swarmauri_transport_https_unicast
```

With `pip`:

```bash
pip install swarmauri_transport_https_unicast
```

## Usage

```python
import asyncio

from swarmauri_transport_https_unicast import (
    HttpsSecurityPolicy,
    HttpsUnicastTransport,
)


async def main() -> None:
    body = b'{"order_id":"ord_1001"}'
    jws_key = {"kind": "raw", "key": b"transport-demo-secret-32-bytes!!", "kid": "body.1"}
    policy = HttpsSecurityPolicy(
        bearer_token="jwt-or-other-bearer-token",
        http_signature_secret="shared-secret",
        request_jws_key=jws_key,
        request_jws_kid="body.1",
        response_jws_key=jws_key,
    )
    transport = HttpsUnicastTransport(
        base_url="https://127.0.0.1:8443",
        verify="/path/to/trust-anchor.pem",
        security_policy=policy,
        require_response_jws=True,
    )

    async with transport.client():
        status, headers, response_body = await transport.request(
            "POST", "/secure/orders", body=body
        )

    print(status, headers["content-type"], response_body)
    print(transport.last_evidence)


asyncio.run(main())
```

Expected output for a service that returns `application/json` and body
`b'{"ok":true}'`:

```text
200 application/json b'{"ok":true}'
HttpsTransportEvidence(status_code=200, response_jws_verified=True, certificate_valid=None, certificate_subject=None, cipher_suite='tls13', cipher_alg='TLS_AES_256_GCM_SHA384')
```

Use `verify_certificate()` when a service has a PEM certificate or chain that
should be validated against explicit trust roots before making transport calls.
Use `allowed_tls_cipher()` on server instrumentation to confirm the negotiated
TLS cipher is within the Swarmauri TLS 1.3 policy.

## Project Links

- Source:
  <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_transport_https_unicast>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>

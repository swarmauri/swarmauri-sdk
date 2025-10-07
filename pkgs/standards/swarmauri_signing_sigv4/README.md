![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_sigv4/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_sigv4" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_sigv4/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_sigv4.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_sigv4/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_sigv4" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_sigv4/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_sigv4" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_sigv4/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_sigv4?label=swarmauri_signing_sigv4&color=green" alt="PyPI - swarmauri_signing_sigv4"/></a>
</p>

---

# Swarmauri Signing SigV4

AWS Signature Version 4 (SigV4) signer and verifier that implements the `ISigning` interface for HTTP requests and raw byte payloads.

## Features

- Canonicalizes HTTP request envelopes according to AWS SigV4 rules
- Derives SigV4 signing keys from AWS credentials and scope information
- Supports both request signing and raw payload HMAC generation/verification
- Returns structured signature metadata (scope, signed headers, canonical hash) for downstream Authorization headers

## Security Notes

- Requires valid AWS-style credentials (`access_key`, `secret_key`, optional `session_token`)
- Verification requires access to the shared secret material; compare signatures externally when AWS performs verification
- Payload canonicalization expects callers to supply the appropriate SHA-256 hash or the `UNSIGNED-PAYLOAD` marker

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_signing_sigv4
```

```bash
uv pip install swarmauri_signing_sigv4
```

```bash
poetry add swarmauri_signing_sigv4
```

## Usage

```python
import asyncio
from swarmauri_signing_sigv4 import SigV4Signing


envelope = {
    "method": "GET",
    "uri": "/",
    "query": {"Action": ["ListUsers"], "Version": ["2010-05-08"]},
    "headers": {
        "host": "iam.amazonaws.com",
        "x-amz-date": "20150830T123600Z",
        "content-type": "application/x-www-form-urlencoded; charset=utf-8",
    },
    "payload_hash": "UNSIGNED-PAYLOAD",
    "amz_date": "20150830T123600Z",
    "scope": {"date": "20150830", "region": "us-east-1", "service": "iam"},
}

key = {"access_key": "AKIDEXAMPLE", "secret_key": "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY"}


async def main() -> None:
    signer = SigV4Signing()
    signatures = await signer.sign_envelope(key, envelope)
    print(signatures[0]["signature"])


asyncio.run(main())
```

When verifying signatures you must provide the shared secret via `opts["secret_key"]` or `require["secret_key"]`.

### Byte payload signing

Use `sign_bytes` / `verify_bytes` when you only need a SigV4-derived HMAC:

```python
payload = b"example"
opts = {"date": "20150830", "region": "us-east-1", "service": "iam"}
signatures = await signer.sign_bytes(key, payload, opts=opts)
assert await signer.verify_bytes(payload, signatures, opts={**opts, "secret_key": key["secret_key"]})
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `SigV4Signing`.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.

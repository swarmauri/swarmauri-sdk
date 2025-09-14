![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_signing_ssh/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_signing_ssh" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_ssh/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_signing_ssh.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ssh/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_signing_ssh" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ssh/">
        <img src="https://img.shields.io/pypi/l/swarmauri_signing_ssh" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_signing_ssh/">
        <img src="https://img.shields.io/pypi/v/swarmauri_signing_ssh?label=swarmauri_signing_ssh&color=green" alt="PyPI - swarmauri_signing_ssh"/></a>

</p>

---

# swarmauri_signing_ssh

An OpenSSH-based signer implementing the `ISigning` interface for detached
signatures over raw bytes and canonicalized envelopes.

Features:
- JSON canonicalization (always available)
- Optional CBOR canonicalization via `cbor2`
- Detached signatures using OpenSSH `ssh-keygen -Y`

## Installation

```bash
pip install swarmauri_signing_ssh
```

## Usage

```python
import asyncio
from swarmauri_signing_ssh import SshEnvelopeSigner

async def main():
    signer = SshEnvelopeSigner()
    key = {"kind": "path", "priv": "/path/to/id_ed25519"}
    payload = b"hello"
    sigs = await signer.sign_bytes(key, payload)
    pub = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA..."
    ok = await signer.verify_bytes(payload, sigs, opts={"pubkeys": [pub]})
    print(ok)

asyncio.run(main())
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `SshEnvelopeSigner`.

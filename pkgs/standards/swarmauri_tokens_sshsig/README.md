![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_sshsig/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_sshsig" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_sshsig/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_sshsig.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_sshsig/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_sshsig" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_sshsig/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_sshsig" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_sshsig/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_sshsig?label=swarmauri_tokens_sshsig&color=green" alt="PyPI - swarmauri_tokens_sshsig"/></a>

</p>

---

# swarmauri_tokens_sshsig

An SSH signature token service for the Swarmauri framework. This service
implements minting and verifying tokens signed with SSH-compatible
algorithms such as Ed25519 and ECDSA P-256.

## Features

- Mint and verify compact `SSHSIG` tokens
- Supports `ssh-ed25519` and `ecdsa-sha2-nistp256`
- Integrates with the Swarmauri token management framework

## Installation

```bash
pip install swarmauri_tokens_sshsig
```

## Usage

```python
from swarmauri_tokens_sshsig import SshSigTokenService
from swarmauri_core.keys import IKeyProvider

key_provider: IKeyProvider = ...  # Provide an implementation of IKeyProvider
svc = SshSigTokenService(key_provider, default_issuer="example.com")

token = await svc.mint({"sub": "alice"}, alg="ssh-ed25519", kid="ed1")
claims = await svc.verify(token, issuer="example.com")
```

The token format uses a compact three-part structure similar to JWT but relies
on SSH signature algorithms. The payload is encoded as deterministic JSON and
bound to a namespace before signing, providing interoperability with existing
SSH key infrastructures.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
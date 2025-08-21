![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

# Swarmauri Signing SSH

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
from swarmauri_signing_ssh import SshEnvelopeSigner

signer = SshEnvelopeSigner()
# create a KeyRef pointing to an SSH private key
```

## Entry Point

The signer registers under the `swarmauri.signings` entry point as `SshEnvelopeSigner`.

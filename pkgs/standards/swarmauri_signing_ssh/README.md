![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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
- Detached signatures powered by OpenSSH `ssh-keygen -Y` for Ed25519, RSA and
  ECDSA keys.
- Accepts private keys from filesystem paths or in-memory PEM blobs.
- JSON canonicalization built in with optional CBOR canonicalization via
  `cbor2`.
- Envelope helpers for canonicalized signing and verification workflows.

## Requirements

- OpenSSH `ssh-keygen` (v8.2 or newer with `-Y` support) must be available on
  `PATH`.
- Install the optional `cbor` extra (`swarmauri_signing_ssh[cbor]`) to enable
  CBOR canonicalization.

## Installation

### pip

```bash
pip install swarmauri_signing_ssh
```

Enable CBOR canonicalization when desired:

```bash
pip install "swarmauri_signing_ssh[cbor]"
```

### uv

```bash
uv add swarmauri_signing_ssh
```

```bash
uv add "swarmauri_signing_ssh[cbor]"
```

### Poetry

```bash
poetry add swarmauri_signing_ssh
```

```bash
poetry add swarmauri_signing_ssh -E cbor
```

## Usage

### Supported key references

Provide the signer with a `KeyRef` dictionary:

- `{"kind": "path", "priv": "/path/to/id_ed25519", "identity": "optional"}`
  references a private key on disk.
- `{"kind": "pem", "priv": "-----BEGIN OPENSSH PRIVATE KEY-----..."}`
  accepts an OpenSSH private key as text/bytes. The key material is written to a
  secure temporary file for signing.

The signer derives the corresponding public key line, fingerprint (`kid`) and
algorithm token automatically.

### Verification options

- Pass one or more OpenSSH public key lines via `opts["pubkeys"]` when calling
  `verify_bytes` or `verify_envelope`. Verification fails immediately when the
  list is missing or empty.
- Override the namespace used by `ssh-keygen -Y` through `opts["namespace"]`
  (defaults to `"file"`).
- Supply the expected signer identity with `opts["identity"]`. Identities
  default to `signer{i}` based on index order.
- Restrict acceptable signatures via the `require` mapping. Supported keys are
  `"algs"`, `"kids"` and `"min_signers"`.

### README example: sign and verify an SSH signature

```python title="README example: sign and verify an SSH signature"
import asyncio
import subprocess
import tempfile
from pathlib import Path

from swarmauri_signing_ssh import SshEnvelopeSigner


async def main() -> bool:
    signer = SshEnvelopeSigner()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        priv_path = tmpdir_path / "id_ed25519"
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(priv_path)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        pubkey_line = priv_path.with_suffix(".pub").read_text(encoding="utf-8").strip()

        key = {"kind": "path", "priv": str(priv_path), "identity": "readme-demo"}
        payload = b"hello ssh signatures"

        signatures = await signer.sign_bytes(key, payload)
        return await signer.verify_bytes(
            payload,
            signatures,
            opts={"pubkeys": [pubkey_line], "identity": "readme-demo"},
        )


if __name__ == "__main__":  # pragma: no cover - README execution path
    print(asyncio.run(main()))
```

Running the script prints `True` once verification succeeds.

### Envelope workflows

Use `sign_envelope` / `verify_envelope` alongside `canonicalize_envelope` to
operate on structured payloads. JSON canonicalization is always available;
enable the `cbor` extra to emit canonical CBOR bytes.

RSA keys default to `sha256` hashing but accept `hashalg="sha512"` via either
the key reference or `opts`. All signatures are detached (`features` include
`"detached_only"`), and multiple signatures can be verified in a single call.

## Entry Point

The signer registers under the `swarmauri.signings` entry point as
`SshEnvelopeSigner`.

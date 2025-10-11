![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tokens_sshcert/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tokens_sshcert" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_sshcert/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tokens_sshcert.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_sshcert/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tokens_sshcert" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_sshcert/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tokens_sshcert" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tokens_sshcert/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tokens_sshcert?label=swarmauri_tokens_sshcert&color=green" alt="PyPI - swarmauri_tokens_sshcert"/></a>

</p>

---

# swarmauri_tokens_sshcert

An OpenSSH certificate token service for the Swarmauri framework. This service
mints and verifies OpenSSH user and host certificates and exposes no JWKS
endpoints.

## Usage

`SshCertTokenService` uses the local `ssh-keygen` utility to mint and verify
OpenSSH certificates. A key provider supplies the certificate authority (CA)
key material used for signing. The typical workflow is:

1. implement or configure an `IKeyProvider` that returns your CA key
2. create the token service
3. mint a certificate for a subject public key
4. verify the certificate before trusting it

```python
import asyncio
import os
import subprocess
import tempfile
from typing import Iterable, Mapping

from swarmauri_tokens_sshcert import SshCertTokenService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_core.key_providers import IKeyProvider


def _generate_keypair() -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "id")
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        priv = open(path, "r", encoding="utf-8").read()
        pub = open(path + ".pub", "r", encoding="utf-8").read()
    return priv, pub


class DummyKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.priv, self.pub = _generate_keypair()
        self.kid = "ca"
        self.version = 1

    async def get_key(
        self, kid: str, version: int | None = None, *, include_secret: bool = False
    ) -> KeyRef:
        material = self.priv if include_secret else None
        return KeyRef(
            kid=self.kid,
            version=self.version,
            type=KeyType.ED25519,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=material,
            public=self.pub,
        )

    async def jwks(self, *, prefix_kids: str | None = None) -> dict:
        return {"keys": []}

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {}


async def main() -> None:
    svc = SshCertTokenService(DummyKeyProvider(), ca_kid="ca")
    _, subj_pub = _generate_keypair()
    cert = await svc.mint(
        {"subject_pub": subj_pub, "principals": ["alice"], "key_id": "demo"},
        alg="ssh-ed25519",
    )
    info = await svc.verify(cert, audience="alice")
    print(info["key_id"])


if __name__ == "__main__":
    asyncio.run(main())
```

The example above mints a certificate for a generated key and verifies it for
the principal `alice`. The service requires the `ssh-keygen` command to be
available on the system path.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.
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
        self,
        kid: str,
        version: int | None = None,
        *,
        include_secret: bool = False,
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

import os
import subprocess
import tempfile
from typing import Iterable, Mapping

import pytest

from swarmauri_tokens_sshcert import SshCertTokenService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_core.keys import IKeyProvider


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

    async def create_key(self, spec) -> KeyRef:  # type: ignore[override]
        raise NotImplementedError

    async def import_key(
        self, spec, material: bytes, *, public: bytes | None = None
    ) -> KeyRef:  # type: ignore[override]
        raise NotImplementedError

    async def rotate_key(
        self, kid: str, *, spec_overrides: dict | None = None
    ) -> KeyRef:  # type: ignore[override]
        raise NotImplementedError

    async def destroy_key(self, kid: str, version: int | None = None) -> bool:  # type: ignore[override]
        raise NotImplementedError

    async def list_versions(self, kid: str) -> tuple[int, ...]:  # type: ignore[override]
        return (self.version,)

    async def get_public_jwk(self, kid: str, version: int | None = None) -> dict:  # type: ignore[override]
        return {}

    async def random_bytes(self, n: int) -> bytes:  # type: ignore[override]
        return os.urandom(n)

    async def hkdf(self, ikm: bytes, *, salt: bytes, info: bytes, length: int) -> bytes:  # type: ignore[override]
        return os.urandom(length)


@pytest.mark.example
@pytest.mark.asyncio
async def test_readme_usage_example() -> None:
    svc = SshCertTokenService(DummyKeyProvider(), ca_kid="ca")
    _, subj_pub = _generate_keypair()
    cert = await svc.mint(
        {"subject_pub": subj_pub, "principals": ["alice"], "key_id": "demo"},
        alg="ssh-ed25519",
    )
    info = await svc.verify(cert, audience="alice")
    assert info["key_id"] == "demo"

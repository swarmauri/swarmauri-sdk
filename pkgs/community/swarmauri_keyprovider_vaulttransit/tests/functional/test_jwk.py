import pytest

from swarmauri_core.crypto.types import KeyRef
from swarmauri_core.keys.types import ExportPolicy
from swarmauri_keyprovider_vaulttransit.VaultTransitKeyProvider import (
    VaultTransitKeyProvider,
)


class DummyProvider(VaultTransitKeyProvider):
    def __init__(self) -> None:  # pragma: no cover - used only in tests
        self._prefer_vault_rng = False

    async def get_key(self, kid, version=None, *, include_secret: bool = False):  # type: ignore[override]
        return KeyRef(
            kid=kid,
            version=1,
            type="OPAQUE",
            uses=(),
            export_policy=ExportPolicy.PUBLIC_ONLY,
            public=None,
            material=None,
            tags={},
        )


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_get_public_jwk_symmetric():
    dummy = DummyProvider()
    jwk = await dummy.get_public_jwk("sym")
    assert jwk["kty"] == "oct" and jwk["alg"] == "A256GCM"

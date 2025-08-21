import pytest

from swarmauri_core.keys.types import ExportPolicy, KeyAlg, KeyClass, KeySpec
from swarmauri_keyproviders import LocalKeyProvider
from swarmauri_keyproviders_mirrored import MirroredKeyProvider


class FailingProvider(LocalKeyProvider):
    async def get_key(self, *args, **kwargs):  # type: ignore[override]
        raise RuntimeError("primary down")


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_failover_reads_from_secondary() -> None:
    primary = FailingProvider()
    secondary = LocalKeyProvider()
    provider = MirroredKeyProvider(primary, secondary, mirror_mode="full")
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        size_bits=None,
        label="func",
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        uses=(),
    )
    ref = await secondary.create_key(spec)
    provider._set_shadow(ref.kid, ref.version, ref)
    got = await provider.get_key(ref.kid, ref.version)
    assert got.kid == ref.kid

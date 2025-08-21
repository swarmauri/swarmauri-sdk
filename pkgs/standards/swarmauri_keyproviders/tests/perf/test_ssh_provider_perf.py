import asyncio

import pytest

from swarmauri_keyproviders import SshKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


@pytest.mark.perf
def test_create_ed25519_perf(benchmark) -> None:
    kp = SshKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )

    async def _create() -> None:
        await kp.create_key(spec)

    benchmark(lambda: asyncio.run(_create()))

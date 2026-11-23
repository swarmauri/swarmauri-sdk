import asyncio

import pytest

from swarmauri_certs_x509 import X509CertService


@pytest.mark.perf
def test_self_signed_perf(benchmark, make_key_ref) -> None:
    svc = X509CertService()
    key = make_key_ref()

    async def _create() -> None:
        await svc.create_self_signed(key, {"CN": "perf"})

    benchmark(lambda: asyncio.run(_create()))

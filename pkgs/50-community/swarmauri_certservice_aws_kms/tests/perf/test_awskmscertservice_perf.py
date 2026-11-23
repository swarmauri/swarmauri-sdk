import asyncio

import pytest


@pytest.mark.perf
@pytest.mark.skip(reason="asn1crypto missing extensions")
def test_sign_cert_perf(service, ca_key_ref, subject_key_ref, benchmark):
    async def coro():
        csr = await service.create_csr(subject_key_ref, {"CN": "perf"})
        await service.sign_cert(csr, ca_key_ref, issuer={"CN": "CA"})

    benchmark(lambda: asyncio.get_event_loop().run_until_complete(coro()))

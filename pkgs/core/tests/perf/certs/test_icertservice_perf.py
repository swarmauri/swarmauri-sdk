import pytest

from swarmauri_core.certs import ICertService


class NoopCertService(ICertService):
    def supports(self):
        return {"features": ()}

    async def create_csr(self, *a, **kw):
        return b""

    async def create_self_signed(self, *a, **kw):
        return b""

    async def sign_cert(self, *a, **kw):
        return b""

    async def verify_cert(self, *a, **kw):
        return {"valid": True}

    async def parse_cert(self, *a, **kw):
        return {}


@pytest.mark.perf
def test_supports_perf(benchmark) -> None:
    svc = NoopCertService()
    result = benchmark(svc.supports)
    assert result == {"features": ()}

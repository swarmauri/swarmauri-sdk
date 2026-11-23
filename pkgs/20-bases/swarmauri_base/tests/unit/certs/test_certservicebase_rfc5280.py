import pytest

from swarmauri_base.certs import CertServiceBase


class Dummy(CertServiceBase):
    def supports(self):
        return {}

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


@pytest.mark.unit
def test_certservicebase_mentions_rfc5280() -> None:
    assert "RFC 5280" in CertServiceBase.__doc__

import pytest

from swarmauri_certs_composite import CompositeCertService
from swarmauri_base.certs.CertServiceBase import CertServiceBase


class SelfSignedOnly(CertServiceBase):
    def supports(self):
        return {"features": ("self_signed",)}

    async def create_self_signed(self, key, subject, **kw):
        return b"self-signed-cert"


class PrimaryCSR(CertServiceBase):
    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, key, subject, **kw):
        return b"primary-csr"


class SecondaryCSR(CertServiceBase):
    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, key, subject, **kw):
        return b"secondary-csr"


@pytest.mark.example
@pytest.mark.asyncio
async def test_composite_usage_example():
    svc = CompositeCertService([SelfSignedOnly(), PrimaryCSR(), SecondaryCSR()])

    features = svc.supports()["features"]
    assert "self_signed" in features and "csr" in features

    cert = await svc.create_self_signed("key", {"CN": "example"})
    assert cert == b"self-signed-cert"

    csr = await svc.create_csr("key", {"CN": "example"})
    assert csr == b"primary-csr"

    csr_override = await svc.create_csr(
        "key", {"CN": "example"}, opts={"backend": "SecondaryCSR"}
    )
    assert csr_override == b"secondary-csr"

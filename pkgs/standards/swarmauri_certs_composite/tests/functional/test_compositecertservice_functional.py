import pytest

from swarmauri_core.certs import ICertService
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
from swarmauri_certs_composite import CompositeCertService


class CSRProvider(ICertService):
    type = "csr"

    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, *a, **kw):
        return b"csr"

    async def create_self_signed(self, *a, **kw):
        return b""

    async def sign_cert(self, *a, **kw):
        return b"csr-cert"

    async def verify_cert(self, *a, **kw):
        return {"valid": True}

    async def parse_cert(self, *a, **kw):
        return {}


class SignProvider(ICertService):
    type = "sign"

    def supports(self):
        return {"features": ("sign_from_csr",)}

    async def create_csr(self, *a, **kw):
        return b""

    async def create_self_signed(self, *a, **kw):
        return b""

    async def sign_cert(self, *a, **kw):
        return b"cert"

    async def verify_cert(self, *a, **kw):
        return {"valid": True}

    async def parse_cert(self, *a, **kw):
        return {}


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_routing_and_override() -> None:
    svc = CompositeCertService([CSRProvider(), SignProvider()])
    key = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    csr = await svc.create_csr(key, {"CN": "example"})
    assert csr == b"csr"
    cert = await svc.sign_cert(b"csr", key)
    assert cert == b"cert"
    cert_override = await svc.sign_cert(b"csr", key, opts={"backend": "csr"})
    assert cert_override == b"csr-cert"

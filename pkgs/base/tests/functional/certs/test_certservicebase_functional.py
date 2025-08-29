import pytest

from swarmauri_base.certs import CertServiceBase
from swarmauri_core.certs.ICertService import SubjectSpec
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


class MinimalCertService(CertServiceBase):
    def supports(self):
        return {"features": ("csr",)}

    async def create_csr(self, key: KeyRef, subject: SubjectSpec, **kw):
        return b"csr"

    async def create_self_signed(self, key: KeyRef, subject: SubjectSpec, **kw):
        return b"cert"

    async def sign_cert(self, csr, ca_key, **kw):
        return b"cert"

    async def verify_cert(self, cert, **kw):
        return {"valid": True}

    async def parse_cert(self, cert, **kw):
        return {"subject": {}}


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_minimal_service_create_csr() -> None:
    svc = MinimalCertService()
    key = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    subject: SubjectSpec = {"CN": "example"}
    csr = await svc.create_csr(key, subject)
    assert csr == b"csr"

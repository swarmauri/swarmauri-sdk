import pytest

from swarmauri_certs_composite import CompositeCertService
from swarmauri_core.certs.ICertService import ICertService
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


class CSRProvider(ICertService):
    type = "CSR"

    def supports(self):
        return {"features": ("csr", "sign_from_csr")}

    async def create_csr(self, key, subject, **kw):
        return b"csr"

    async def sign_cert(self, csr, ca_key, **kw):
        return b"cert-from-csr"

    async def create_self_signed(self, *args, **kwargs):  # pragma: no cover - not used
        raise NotImplementedError

    async def verify_cert(self, *args, **kwargs):  # pragma: no cover - not used
        raise NotImplementedError

    async def parse_cert(self, *args, **kwargs):  # pragma: no cover - not used
        raise NotImplementedError


class SelfSignedProvider(ICertService):
    type = "SELF"

    def supports(self):
        return {"features": ("self_signed", "sign_from_csr")}

    async def create_self_signed(self, key, subject, **kw):
        return b"self-signed"

    async def sign_cert(self, csr, ca_key, **kw):
        return b"cert-signed"

    async def create_csr(self, *args, **kwargs):  # pragma: no cover - not used
        raise NotImplementedError

    async def verify_cert(self, *args, **kwargs):  # pragma: no cover - not used
        raise NotImplementedError

    async def parse_cert(self, *args, **kwargs):  # pragma: no cover - not used
        raise NotImplementedError


@pytest.mark.asyncio
@pytest.mark.example
async def test_usage_example():
    key = KeyRef(
        kid="k1",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.NONE,
    )
    subject = {"CN": "example.com"}

    svc = CompositeCertService([CSRProvider(), SelfSignedProvider()])

    csr = await svc.create_csr(key, subject)
    assert csr == b"csr"

    cert = await svc.sign_cert(csr, key, opts={"backend": "SELF"})
    assert cert == b"cert-signed"

    self_signed = await svc.create_self_signed(key, subject)
    assert self_signed == b"self-signed"

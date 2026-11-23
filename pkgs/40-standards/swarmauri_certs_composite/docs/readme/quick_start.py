import asyncio

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


async def main():
    svc = CompositeCertService(
        [SelfSignedOnly(), PrimaryCSR(), SecondaryCSR()]
    )

    features = svc.supports()["features"]
    print("Advertised features:", sorted(features))

    cert = await svc.create_self_signed("key", {"CN": "example"})
    print("Self-signed cert:", cert)

    csr = await svc.create_csr("key", {"CN": "example"})
    print("CSR from primary provider:", csr)

    csr_override = await svc.create_csr(
        "key", {"CN": "example"}, opts={"backend": "SecondaryCSR"}
    )
    print("CSR via explicit backend override:", csr_override)


if __name__ == "__main__":
    asyncio.run(main())

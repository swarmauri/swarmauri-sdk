import pytest
from cryptography import x509
from cryptography.x509.oid import NameOID


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_self_signed(service_keyref):
    svc, key = service_keyref
    cert_pem = await svc.create_self_signed(key, {"CN": "example.com"})
    cert = x509.load_pem_x509_certificate(cert_pem)
    cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    assert cn == "example.com"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_csr(service_keyref):
    svc, key = service_keyref
    csr_pem = await svc.create_csr(key, {"CN": "example.com"})
    csr = x509.load_pem_x509_csr(csr_pem)
    assert csr.subject.rfc4514_string() == "CN=example.com"

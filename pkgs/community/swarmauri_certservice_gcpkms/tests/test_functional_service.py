import pytest
from cryptography import x509


@pytest.mark.asyncio
@pytest.mark.functional
async def test_sign_and_verify(service_keyref):
    svc, key = service_keyref
    csr = await svc.create_csr(key, {"CN": "example.com"})
    cert_pem = await svc.sign_cert(csr, key)
    result = await svc.verify_cert(cert_pem, trust_roots=[cert_pem])
    assert result["valid"]
    cert = x509.load_pem_x509_certificate(cert_pem)
    assert cert.subject == cert.issuer

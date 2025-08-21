import pytest


@pytest.mark.xfail(reason="asn1crypto missing extensions", raises=AttributeError)
@pytest.mark.asyncio
async def test_sign_and_verify(service, ca_key_ref, subject_key_ref):
    ca_cert = await service.create_self_signed(ca_key_ref, {"CN": "CA"})
    csr_pem = await service.create_csr(subject_key_ref, {"CN": "leaf"})
    cert_pem = await service.sign_cert(csr_pem, ca_key_ref, ca_cert=ca_cert)
    result = await service.verify_cert(cert_pem, trust_roots=[ca_cert])
    assert result["valid"] is True
    parsed = await service.parse_cert(cert_pem)
    assert parsed["issuer"].startswith("CN=CA")

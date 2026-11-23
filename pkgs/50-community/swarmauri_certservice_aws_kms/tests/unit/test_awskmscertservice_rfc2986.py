import pytest
from cryptography import x509
from cryptography.x509.oid import NameOID


@pytest.mark.asyncio
async def test_create_csr_subject(service, subject_key_ref):
    csr_pem = await service.create_csr(subject_key_ref, {"CN": "example.com"})
    csr = x509.load_pem_x509_csr(csr_pem)
    cn = csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    assert cn == "example.com"

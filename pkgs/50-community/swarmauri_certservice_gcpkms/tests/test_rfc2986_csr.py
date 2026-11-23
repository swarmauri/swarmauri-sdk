"""Tests for RFC 2986 CSR subject handling."""

import pytest
from cryptography import x509


@pytest.mark.asyncio
async def test_csr_subject(service_keyref):
    svc, key = service_keyref
    csr_pem = await svc.create_csr(key, {"CN": "example.com"})
    csr = x509.load_pem_x509_csr(csr_pem)
    assert csr.subject.rfc4514_string() == "CN=example.com"

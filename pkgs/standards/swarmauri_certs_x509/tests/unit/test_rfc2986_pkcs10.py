"""RFC 2986: PKCS#10 Certification Request Syntax."""

import asyncio

from swarmauri_certs_x509 import X509CertService


def test_csr_rfc2986(make_key_ref) -> None:
    svc = X509CertService()
    key = make_key_ref()
    csr = asyncio.run(svc.create_csr(key, {"CN": "rfc2986"}))
    assert b"BEGIN CERTIFICATE REQUEST" in csr

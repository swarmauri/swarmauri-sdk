"""RFC 5280: Basic certificate path validation."""

import asyncio

from swarmauri_certs_x509 import X509CertService


def test_verify_chain_rfc5280(make_key_ref) -> None:
    svc = X509CertService()
    ca_key = make_key_ref()
    csr_key = make_key_ref()
    csr = asyncio.run(svc.create_csr(csr_key, {"CN": "leaf"}))
    ca_cert = asyncio.run(
        svc.create_self_signed(
            ca_key, {"CN": "ca"}, extensions={"basic_constraints": {"ca": True}}
        )
    )
    leaf_cert = asyncio.run(svc.sign_cert(csr, ca_key, ca_cert=ca_cert))
    result = asyncio.run(svc.verify_cert(leaf_cert, trust_roots=[ca_cert]))
    assert result["valid"] is True

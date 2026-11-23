import asyncio


from swarmauri_certs_x509 import X509CertService


def test_verify_functional(make_key_ref) -> None:
    svc = X509CertService()
    key = make_key_ref()
    cert = asyncio.run(svc.create_self_signed(key, {"CN": "func"}))
    result = asyncio.run(svc.verify_cert(cert, trust_roots=[cert]))
    assert result["valid"] is True


def test_invalid_chain_functional(make_key_ref) -> None:
    svc = X509CertService()
    key = make_key_ref()
    cert = asyncio.run(svc.create_self_signed(key, {"CN": "bad"}))
    root_key = make_key_ref()
    root_cert = asyncio.run(svc.create_self_signed(root_key, {"CN": "root"}))
    result = asyncio.run(svc.verify_cert(cert, trust_roots=[root_cert]))
    assert result["valid"] is False

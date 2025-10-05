import pytest

from swarmauri_core.pop import BindType, CnfBinding, PoPBindingError, PoPParseError, VerifyPolicy
from swarmauri_base.pop import RequestContext, sha256_b64u

from swarmauri_pop_x509 import X509PoPVerifier


@pytest.mark.asyncio
async def test_verify_core_enforces_x5t_binding():
    verifier = X509PoPVerifier()
    context = RequestContext(method="GET", htu="https://example.com", policy=VerifyPolicy())
    cnf = CnfBinding(bind_type=BindType.JKT, value_b64u="")

    with pytest.raises(PoPBindingError):
        await verifier._verify_core(
            proof="",
            context=context,
            cnf=cnf,
            replay=None,
            keys=None,
            extras={"peer_cert_der": b"dummy"},
        )


@pytest.mark.asyncio
async def test_verify_core_requires_peer_cert_extra():
    verifier = X509PoPVerifier()
    context = RequestContext(method="GET", htu="https://example.com", policy=VerifyPolicy())
    cnf = CnfBinding(bind_type=BindType.X5T_S256, value_b64u="")

    with pytest.raises(PoPParseError):
        await verifier._verify_core(
            proof="",
            context=context,
            cnf=cnf,
            replay=None,
            keys=None,
            extras={},
        )


@pytest.mark.asyncio
async def test_verify_core_validates_peer_cert_type():
    verifier = X509PoPVerifier()
    context = RequestContext(method="GET", htu="https://example.com", policy=VerifyPolicy())
    cnf = CnfBinding(bind_type=BindType.X5T_S256, value_b64u="")

    with pytest.raises(PoPParseError):
        await verifier._verify_core(
            proof="",
            context=context,
            cnf=cnf,
            replay=None,
            keys=None,
            extras={"peer_cert_der": "not-bytes"},
        )


@pytest.mark.asyncio
async def test_verify_core_detects_thumbprint_mismatch():
    verifier = X509PoPVerifier()
    context = RequestContext(method="GET", htu="https://example.com", policy=VerifyPolicy())
    cnf = CnfBinding(bind_type=BindType.X5T_S256, value_b64u="unexpected")

    with pytest.raises(PoPBindingError):
        await verifier._verify_core(
            proof="",
            context=context,
            cnf=cnf,
            replay=None,
            keys=None,
            extras={"peer_cert_der": b"certificate"},
        )


@pytest.mark.asyncio
async def test_verify_core_accepts_matching_thumbprint():
    verifier = X509PoPVerifier()
    context = RequestContext(method="GET", htu="https://example.com", policy=VerifyPolicy())
    cert_bytes = b"certificate"
    thumbprint = sha256_b64u(cert_bytes)
    cnf = CnfBinding(bind_type=BindType.X5T_S256, value_b64u=thumbprint)

    await verifier._verify_core(
        proof="",
        context=context,
        cnf=cnf,
        replay=None,
        keys=None,
        extras={"peer_cert_der": cert_bytes},
    )

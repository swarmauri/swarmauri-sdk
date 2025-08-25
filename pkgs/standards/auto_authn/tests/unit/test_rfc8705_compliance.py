import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from auto_authn.v2.jwtoken import JWTCoder


@pytest.mark.unit
@pytest.mark.xfail(reason="RFC 8705 support planned")
def test_jwt_includes_cnf_claim_for_mtls():
    """JWTs should embed cnf.x5t#S256 when mTLS is used."""
    private_key_obj = Ed25519PrivateKey.generate()
    public_key_obj = private_key_obj.public_key()

    private_pem = private_key_obj.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key_obj.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    coder = JWTCoder(private_pem, public_pem)
    token = coder.sign(sub="alice", tid="tenant")
    payload = coder.decode(token)

    assert "cnf" in payload

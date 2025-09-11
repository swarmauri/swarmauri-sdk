from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import pytest

from swarmauri_keyprovider_aws_kms import AwsKmsKeyProvider


@pytest.mark.i9n
def test_public_jwk_from_der_rsa():
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    der = priv.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    provider = AwsKmsKeyProvider(region="us-east-1")
    jwk = provider._public_jwk_from_der(der, "testkid")
    assert jwk["kty"] == "RSA"
    assert jwk["kid"] == "testkid"

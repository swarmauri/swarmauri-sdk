import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
from swarmauri_certservice_aws_kms import AwsKmsCertService


class _KmsMock:
    def __init__(self, priv: rsa.RSAPrivateKey) -> None:
        self._priv = priv
        self._pub = priv.public_key()

    def get_public_key(self, KeyId: str):  # pragma: no cover - simple passthrough
        spki = self._pub.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        return {"PublicKey": spki, "KeySpec": "RSA_2048"}

    def sign(self, KeyId: str, Message: bytes, MessageType: str, SigningAlgorithm: str):
        signature = self._priv.sign(
            Message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=hashes.SHA256().digest_size,
            ),
            hashes.SHA256(),
        )
        return {"Signature": signature}


@pytest.fixture()
def ca_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture()
def service(ca_key: rsa.RSAPrivateKey) -> AwsKmsCertService:
    svc = AwsKmsCertService(default_sig_alg="RSA-SHA256")
    svc._client = lambda: _KmsMock(ca_key)
    return svc


@pytest.fixture()
def ca_key_ref() -> KeyRef:
    return KeyRef(
        kid="test",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.NONE,
        tags={"aws_kms_key_id": "test"},
    )


@pytest.fixture()
def subject_key_ref() -> KeyRef:
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = priv.private_bytes(
        Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()
    )
    return KeyRef(
        kid="subj",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )

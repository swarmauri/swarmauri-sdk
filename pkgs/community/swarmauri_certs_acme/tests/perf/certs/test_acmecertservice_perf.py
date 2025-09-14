import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from swarmauri_certs_acme import AcmeCertService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


@pytest.mark.perf
def test_supports_perf(benchmark) -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
    account = KeyRef(
        kid="acc",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=priv,
    )
    svc = AcmeCertService(account_key=account)
    result = benchmark(svc.supports)
    assert "acme" in result["features"]

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from swarmauri_certservice_gcpkms import GcpKmsCertService
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
import importlib

mod = importlib.import_module("swarmauri_certservice_gcpkms.GcpKmsCertService")


class _FakeClient:
    def __init__(self, priv):
        self._pem = (
            priv.public_key()
            .public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("utf-8")
        )

    def get_public_key(self, request):
        class Pub:
            def __init__(self, pem):
                self.pem = pem
                self.algorithm = type("Alg", (), {"name": "RSA_SIGN_PKCS1_2048_SHA256"})

        return Pub(self._pem)


@pytest.fixture()
def service_keyref(monkeypatch):
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    client = _FakeClient(priv)
    svc = GcpKmsCertService()
    monkeypatch.setattr(GcpKmsCertService, "_client_or_new", lambda self: client)
    monkeypatch.setattr(mod, "_make_kms_private_key", lambda client, version: priv)
    keyref = KeyRef(
        kid="projects/test/cryptoKeyVersions/1",
        version="1",
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.NONE,
        tags={"gcp_kms_key_version": "projects/test/cryptoKeyVersions/1"},
    )
    return svc, keyref

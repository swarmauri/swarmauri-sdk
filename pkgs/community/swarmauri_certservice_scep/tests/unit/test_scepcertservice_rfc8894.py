import pytest
import requests

from swarmauri_certservice_scep import ScepCertService
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


class DummyResp:
    def __init__(self, content=b"cert"):
        self.content = content

    def raise_for_status(self) -> None:  # pragma: no cover - trivial
        return None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_sign_cert_rfc8894(monkeypatch) -> None:
    svc = ScepCertService("https://scep.test")

    def fake_post(url, data):
        assert url == "https://scep.test/pkiclient.exe?operation=PKIOperation"
        assert data == b"csr"
        return DummyResp()

    monkeypatch.setattr(requests, "post", fake_post)
    ca_key = KeyRef(
        kid="k",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    cert = await svc.sign_cert(b"csr", ca_key)
    assert cert == b"cert"

import pytest

from swarmauri_keyprovider_gcpkms.GcpKmsKeyProvider import GcpKmsKeyProvider


class DummyCreds:
    token = "token"
    valid = True

    def refresh(self, request):
        return None


@pytest.fixture
def provider(monkeypatch):
    def fake_default(scopes=None):
        return DummyCreds(), None

    monkeypatch.setattr("google.auth.default", fake_default)
    return GcpKmsKeyProvider(project_id="p", location_id="l", key_ring_id="r")


@pytest.mark.functional
@pytest.mark.asyncio
async def test_hkdf_derivation(provider):
    key = await provider.hkdf(b"input", salt=b"salt", info=b"info", length=32)
    assert len(key) == 32

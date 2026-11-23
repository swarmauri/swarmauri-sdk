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


@pytest.mark.unit
def test_type(provider):
    assert provider.type == "GcpKmsKeyProvider"


@pytest.mark.unit
def test_id_is_str(provider):
    assert isinstance(provider.id, str)


@pytest.mark.functional
@pytest.mark.asyncio
async def test_random_bytes(provider):
    assert len(await provider.random_bytes(32)) == 32

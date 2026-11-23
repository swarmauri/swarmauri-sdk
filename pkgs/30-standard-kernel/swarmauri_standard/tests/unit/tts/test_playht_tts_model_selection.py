import httpx
import pytest

from swarmauri_standard.llms.PlayHTModel import PlayHTModel

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "credentials", [{}, {"api_key": "old-key", "user_id": "old-user"}]
)
def test_retired_provider_fails_before_network(monkeypatch, credentials):
    def forbidden(*args, **kwargs):
        pytest.fail("Retired provider attempted network access")

    monkeypatch.setattr(httpx, "Client", forbidden)
    monkeypatch.setattr(httpx, "AsyncClient", forbidden)
    with pytest.warns(DeprecationWarning, match="Play.ht"):
        with pytest.raises(RuntimeError, match="OpenaiTTS"):
            PlayHTModel(**credentials)

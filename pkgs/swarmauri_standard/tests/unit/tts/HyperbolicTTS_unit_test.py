"""Retirement must not inspect credentials or contact a provider."""

import httpx
import pytest
from swarmauri_standard.tts.HyperbolicTTS import HyperbolicTTS

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("settings", [{}, {"api_key": "old-key"}])
def test_retired_provider_fails_before_network(monkeypatch, settings):
    def forbidden(*args, **kwargs):
        pytest.fail("Retired provider attempted HTTP")

    monkeypatch.setattr(httpx, "Client", forbidden)
    monkeypatch.setattr(httpx, "AsyncClient", forbidden)
    with pytest.warns(FutureWarning, match="decommissioned"):
        with pytest.raises(RuntimeError, match="decommissioned"):
            HyperbolicTTS(**settings)


@pytest.mark.asyncio
async def test_validation_bypass_cannot_reenable_requests(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Retired provider attempted HTTP")

    monkeypatch.setattr(httpx, "Client", forbidden)
    monkeypatch.setattr(httpx, "AsyncClient", forbidden)
    provider = HyperbolicTTS.model_construct()
    for operation in [
        lambda: provider.predict("hello"),
        lambda: provider.batch({"hello": "out.mp3"}),
        lambda: provider.stream("hello"),
    ]:
        with pytest.warns(FutureWarning, match="decommissioned"):
            with pytest.raises(RuntimeError):
                operation()
    for operation in [
        lambda: provider.apredict("hello"),
        lambda: provider.abatch({"hello": "out.mp3"}),
        lambda: provider.astream("hello"),
    ]:
        with pytest.warns(FutureWarning, match="decommissioned"):
            with pytest.raises(RuntimeError):
                await operation()

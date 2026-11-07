from importlib.metadata import entry_points

import pytest
from swarmauri_core.model_providers import IProviderAuth, IProviderEndpoint

from swarmauri_provider_openrouter import (
    OpenRouterModelCatalog,
    OpenRouterProvider,
    OpenRouterProviderPreferences,
)


@pytest.mark.unit
def test_provider_builds_authorized_capability_config():
    provider = OpenRouterProvider(
        api_key="secret",
        site_url="https://example.com",
        app_name="app",
    )
    config = provider.connection_config(
        "chat.completions", model="openai/gpt-4o-mini"
    )

    assert isinstance(provider.auth, IProviderAuth)
    assert isinstance(provider.endpoints, IProviderEndpoint)
    assert config.endpoint == "https://openrouter.ai/api/v1/chat/completions"
    assert config.transport_options["model"] == "openai/gpt-4o-mini"
    assert provider.authorize(config) == {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer secret",
        "HTTP-Referer": "https://example.com",
        "X-OpenRouter-Title": "app",
    }
    assert "secret" not in provider.model_dump_json()
    assert "secret" not in config.model_dump_json()


@pytest.mark.unit
def test_provider_rejects_unknown_capability():
    with pytest.raises(ValueError, match="unknown"):
        OpenRouterProvider().connection_config("unknown")


@pytest.mark.unit
def test_catalog_loads_and_filters_provider_response():
    catalog = OpenRouterModelCatalog()
    catalog.load_response(
        {
            "data": [
                {
                    "id": "text/model",
                    "architecture": {"output_modalities": ["text"]},
                },
                {
                    "id": "image/model",
                    "architecture": {"output_modalities": ["image"]},
                },
            ]
        }
    )

    assert catalog.list_model_ids() == ["text/model", "image/model"]
    assert catalog.list_model_ids(output_modalities="image") == ["image/model"]


@pytest.mark.unit
def test_routing_preferences_are_strict_and_serializable():
    preferences = OpenRouterProviderPreferences(
        order=["OpenAI"], data_collection="deny", zdr=True
    )
    assert preferences.model_dump(exclude_none=True)["order"] == ["OpenAI"]
    with pytest.raises(ValueError):
        OpenRouterProviderPreferences(unsupported=True)


@pytest.mark.unit
def test_provider_entry_point_is_registered():
    matches = [
        entry
        for entry in entry_points(group="swarmauri.model_providers")
        if entry.name == "OpenRouterProvider"
    ]
    assert len(matches) == 1
    assert matches[0].load().__name__ == "OpenRouterProvider"

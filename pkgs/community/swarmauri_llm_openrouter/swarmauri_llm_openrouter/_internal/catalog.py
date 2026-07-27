"""Discover current OpenRouter models and their capabilities."""

from typing import Any

from pydantic import SecretStr

from .transport import OpenRouterTransport


class OpenRouterModelCatalog:
    """Query OpenRouter model catalogs without constructor-time network I/O."""

    def __init__(self, transport: OpenRouterTransport):
        self._transport = transport

    @classmethod
    def from_api_key(
        cls,
        api_key: str | SecretStr,
        *,
        base_url: str = "https://openrouter.ai/api/v1",
        site_url: str | None = None,
        app_name: str | None = None,
        timeout: float = 600.0,
    ) -> "OpenRouterModelCatalog":
        """Create a standalone catalog client before selecting a model."""
        secret = (
            api_key.get_secret_value()
            if isinstance(api_key, SecretStr)
            else api_key
        )
        headers = {"Authorization": f"Bearer {secret}"}
        if site_url:
            headers["HTTP-Referer"] = site_url
        if app_name:
            headers["X-OpenRouter-Title"] = app_name
        return cls(OpenRouterTransport(base_url, headers, timeout))

    def list_models(
        self, *, output_modalities: str | None = None
    ) -> list[dict[str, Any]]:
        """Return models, optionally filtered by output modality."""
        path = "models"
        if output_modalities:
            path += f"?output_modalities={output_modalities}"
        return self._transport.request("GET", path).json()["data"]

    def list_model_ids(
        self, *, output_modalities: str | None = None
    ) -> list[str]:
        """Return current model IDs for an exact downstream allowlist."""
        return [
            model["id"]
            for model in self.list_models(output_modalities=output_modalities)
        ]

    async def alist_models(
        self, *, output_modalities: str | None = None
    ) -> list[dict[str, Any]]:
        """Return models asynchronously."""
        path = "models"
        if output_modalities:
            path += f"?output_modalities={output_modalities}"
        response = await self._transport.arequest("GET", path)
        return response.json()["data"]

    async def alist_model_ids(
        self, *, output_modalities: str | None = None
    ) -> list[str]:
        """Return current model IDs asynchronously."""
        models = await self.alist_models(output_modalities=output_modalities)
        return [model["id"] for model in models]

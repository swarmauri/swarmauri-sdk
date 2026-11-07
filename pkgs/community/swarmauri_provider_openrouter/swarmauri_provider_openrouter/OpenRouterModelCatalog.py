from collections.abc import Iterable
from typing import Any, Literal

from swarmauri_base.model_providers.ModelCatalogBase import ModelCatalogBase


class OpenRouterModelCatalog(ModelCatalogBase):
    models: dict[str, Any] = {
        "openrouter/auto": {
            "id": "openrouter/auto",
            "name": "openrouter/auto",
            "capabilities": ["chat_completions", "streaming", "tools"],
        }
    }
    type: Literal["OpenRouterModelCatalog"] = "OpenRouterModelCatalog"

    def load_response(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        models = [item for item in payload.get("data", []) if item.get("id")]
        self.models = {item["id"]: dict(item) for item in models}
        return models

    def list_models(
        self, *, output_modalities: str | None = None
    ) -> Iterable[Any]:
        models = list(self.models.values())
        if output_modalities is None:
            return models
        return [
            model
            for model in models
            if output_modalities
            in (model.get("architecture", {}).get("output_modalities") or [])
        ]

    def list_model_ids(
        self, *, output_modalities: str | None = None
    ) -> list[str]:
        return [
            model.get("id") or model["name"]
            for model in self.list_models(output_modalities=output_modalities)
        ]

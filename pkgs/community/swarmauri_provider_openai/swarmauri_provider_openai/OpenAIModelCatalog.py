from typing import Literal

from swarmauri_base.model_providers.ModelCatalogBase import ModelCatalogBase


class OpenAIModelCatalog(ModelCatalogBase):
    models: dict = {
        "gpt-realtime": {
            "name": "gpt-realtime",
            "input_modalities": ["text", "audio", "image"],
            "output_modalities": ["text", "audio"],
            "features": ["realtime", "tools", "interruption"],
        }
    }
    type: Literal["OpenAIModelCatalog"] = "OpenAIModelCatalog"

from typing import Literal

from swarmauri_base.model_providers.ModelCatalogBase import ModelCatalogBase


class GeminiModelCatalog(ModelCatalogBase):
    models: dict = {
        "gemini-3.1-flash-live-preview": {
            "name": "gemini-3.1-flash-live-preview",
            "input_modalities": ["text", "audio", "image", "video"],
            "output_modalities": ["audio", "text"],
            "features": ["realtime", "tools", "transcription"],
        }
    }
    type: Literal["GeminiModelCatalog"] = "GeminiModelCatalog"

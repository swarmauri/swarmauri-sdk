from typing import Literal

from swarmauri_base.model_providers.ModelCatalogBase import ModelCatalogBase


class XAIModelCatalog(ModelCatalogBase):
    models: dict = {
        "grok-4.3": {
            "name": "grok-4.3",
            "capabilities": [
                "chat_completions",
                "multimodal_input",
                "streaming",
                "tools",
            ],
        }
    }
    type: Literal["XAIModelCatalog"] = "XAIModelCatalog"

from typing import Literal

from swarmauri_base.model_providers.ModelCatalogBase import ModelCatalogBase


class QwenModelCatalog(ModelCatalogBase):
    models: dict = {
        "qwen-omni-turbo-realtime": {
            "name": "qwen-omni-turbo-realtime",
            "features": ["realtime", "audio", "tools"],
        }
    }
    type: Literal["QwenModelCatalog"] = "QwenModelCatalog"

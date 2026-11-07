from typing import Literal

from swarmauri_base.model_providers.ModelCatalogBase import ModelCatalogBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ModelCatalogBase, "QwenModelCatalog")
class QwenModelCatalog(ModelCatalogBase):
    models: dict = {
        "qwen-omni-turbo-realtime": {
            "name": "qwen-omni-turbo-realtime",
            "features": ["realtime", "audio", "tools"],
        }
    }
    type: Literal["QwenModelCatalog"] = "QwenModelCatalog"

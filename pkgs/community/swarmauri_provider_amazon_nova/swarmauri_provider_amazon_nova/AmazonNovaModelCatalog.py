from typing import Literal

from swarmauri_base.model_providers.ModelCatalogBase import ModelCatalogBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ModelCatalogBase, "AmazonNovaModelCatalog")
class AmazonNovaModelCatalog(ModelCatalogBase):
    models: dict = {
        "amazon.nova-sonic-v1:0": {
            "name": "amazon.nova-sonic-v1:0",
            "features": ["realtime", "audio", "tools", "http2"],
        }
    }
    type: Literal["AmazonNovaModelCatalog"] = "AmazonNovaModelCatalog"

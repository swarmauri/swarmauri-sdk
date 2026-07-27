from typing import Literal

from swarmauri_base.model_providers.ModelCatalogBase import ModelCatalogBase


class AmazonNovaModelCatalog(ModelCatalogBase):
    models: dict = {
        "amazon.nova-sonic-v1:0": {
            "name": "amazon.nova-sonic-v1:0",
            "features": ["realtime", "audio", "tools", "http2"],
        }
    }
    type: Literal["AmazonNovaModelCatalog"] = "AmazonNovaModelCatalog"

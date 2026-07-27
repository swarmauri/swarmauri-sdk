from typing import Literal
from swarmauri_base.model_providers import ModelCatalogBase


class XAIModelCatalog(ModelCatalogBase):
    models: dict = {}
    type: Literal["XAIModelCatalog"] = "XAIModelCatalog"

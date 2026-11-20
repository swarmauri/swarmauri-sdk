from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_model()
class StoreConfig(ComponentBase):
    type: Literal["StoreConfig"] = "StoreConfig"
    name: str

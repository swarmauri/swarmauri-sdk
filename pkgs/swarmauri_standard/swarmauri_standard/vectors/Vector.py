from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vectors.VectorBase import VectorBase


@ComponentBase.register_type(VectorBase, "Vector")
class Vector(VectorBase):
    type: Literal["Vector"] = "Vector"

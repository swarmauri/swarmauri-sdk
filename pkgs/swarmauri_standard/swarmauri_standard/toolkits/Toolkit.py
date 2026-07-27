from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase


@ComponentBase.register_type(ToolkitBase, "Toolkit")
class Toolkit(ToolkitBase):
    type: Literal["Toolkit"] = "Toolkit"

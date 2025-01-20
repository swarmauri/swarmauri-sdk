from typing import Literal
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_core.ComponentBase import ComponentBase

@ComponentBase.register_type(ToolkitBase, 'Toolkit')
class Toolkit(ToolkitBase):
    type: Literal['Toolkit'] = 'Toolkit'
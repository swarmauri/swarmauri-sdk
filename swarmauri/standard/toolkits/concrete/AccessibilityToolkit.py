from typing import Literal
from swarmauri.standard.tools.concrete.TextLengthTool import TextLengthTool
from swarmauri.standard.toolkits.base.ToolkitBase import ToolkitBase

class AccessibilityToolkit(ToolkitBase):
    type: Literal['AccessibilityToolkit'] = 'AccessibilityToolkit'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_tool(TextLengthTool(name='TextLengthTool'))
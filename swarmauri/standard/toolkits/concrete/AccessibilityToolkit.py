from typing import Literal
from swarmauri.standard.tools.concrete.AutomatedReadabilityIndexTool import AutomatedReadabilityIndexTool
from swarmauri.standard.tools.concrete.ColemanLiauIndexTool import ColemanLiauIndexTool
from swarmauri.standard.tools.concrete.FleschKincaidTool import FleschKincaidTool
from swarmauri.standard.tools.concrete.FleschReadingEaseTool import FleschReadingEaseTool
from swarmauri.standard.tools.concrete.GunningFogTool import GunningFogTool
from swarmauri.standard.toolkits.base.ToolkitBase import ToolkitBase

class AccessibilityToolkit(ToolkitBase):
    type: Literal['AccessibilityToolkit'] = 'AccessibilityToolkit'
    resource: Literal['AccessibilityToolkit'] = 'AccessibilityToolkit'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools = []
        self.add_tool(AutomatedReadabilityIndexTool(name='AutomatedReadabilityIndexTool'))
        self.add_tool(ColemanLiauIndexTool(name='ColemanLiauIndexTool'))
        self.add_tool(FleschKincaidTool(name='FleschKincaidTool'))
        self.add_tool(FleschReadingEaseTool(name='FleschReadingEaseTool'))
        self.add_tool(GunningFogTool(name='GunningFogTool'))

    def add_tool(self, tool):
        self.tools.append(tool)

    def get_tool_names(self):
        # Returns a list of tool names in the toolkit
        return [tool.name for tool in self.tools]

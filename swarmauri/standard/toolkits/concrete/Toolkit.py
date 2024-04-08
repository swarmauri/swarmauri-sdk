from typing import Dict
from ..base.ToolkitBase import ToolkitBase
from ....core.tools.ITool import ITool

class Toolkit(ToolkitBase):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    def __init__(self, initial_tools: Dict[str, ITool] = None):
        """
        Initialize the Toolkit with an optional dictionary of initial tools.
        """
        
        super().__init__(initial_tools)
    
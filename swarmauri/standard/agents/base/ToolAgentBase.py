from abc import ABC
from swarmauri.core.agents.IAgentToolkit import IAgentToolkit
from swarmauri.core.toolkits.IToolkit import IToolkit


class ToolAgentBase(IAgentToolkit, ABC):
    
    def __init__(self, toolkit: IToolkit):
        self._toolkit = toolkit

    @property
    def toolkit(self) -> IToolkit:
        return self._toolkit
    
    @toolkit.setter
    def toolkit(self, value) -> None:
        self._toolkit = value        

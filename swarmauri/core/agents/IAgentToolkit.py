from abc import ABC, abstractmethod
from swarmauri.core.toolkits.IToolkit import IToolkit


class IAgentToolkit(ABC):

    @property
    @abstractmethod
    def toolkit(self) -> IToolkit:
        pass
    
    @toolkit.setter
    @abstractmethod
    def toolkit(self) -> IToolkit:
        pass
    

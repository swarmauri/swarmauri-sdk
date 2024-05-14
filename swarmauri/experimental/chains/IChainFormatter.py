from abc import ABC, abstractmethod
from core.chains.IChainStep import IChainStep

class IChainFormatter(ABC):
    @abstractmethod
    def format_output(self, step: IChainStep, output: Any) -> str:
        """Format the output of a specific chain step."""
        pass
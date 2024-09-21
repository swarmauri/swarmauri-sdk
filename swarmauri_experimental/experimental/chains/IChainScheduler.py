from abc import ABC, abstractmethod
from swarmauri.core.chains.IChain import IChain

class IChainScheduler(ABC):
    @abstractmethod
    def schedule_chain(self, chain: IChain, schedule: str) -> None:
        """Schedule the execution of the given chain."""
        pass
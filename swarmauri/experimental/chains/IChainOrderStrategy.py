from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.chains.IChainStep import IChainStep

# Defines how chain steps are ordered
class IChainOrderStrategy(ABC):
    @abstractmethod
    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        pass
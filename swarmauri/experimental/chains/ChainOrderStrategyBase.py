from typing import List
from swarmauri.core.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainOrderStrategyBase(IChainOrderStrategy):
    """
    A base implementation of the IChainOrderStrategy interface.
    """

    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        """
        Default implementation doesn't reorder steps but must be overridden by specific strategies.
        """
        return steps
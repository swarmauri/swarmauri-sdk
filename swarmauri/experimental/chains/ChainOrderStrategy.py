from typing import List
from swarmauri.core.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class ChainOrderStrategy(IChainOrderStrategy):
    def order_steps(self, steps: List[IChainStep]) -> List[IChainStep]:
        """
        Orders the chain steps in reverse order.

        Args:
            steps (List[IChainStep]): The original list of chain steps to be ordered.

        Returns:
            List[IChainStep]: List of chain steps in order.
        """
        # Reverse the list of steps.
        steps = list(steps)
        return steps
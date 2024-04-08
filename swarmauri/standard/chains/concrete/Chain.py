from typing import List, Any

from swarmauri.core.chains.IChainStep import IChainStep
from swarmauri.core.chains.IChainOrderStrategy import IChainOrderStrategy
from swarmauri.standard.chains.base.ChainBase import ChainBase
from swarmauri.standard.chains.concrete.ChainProcessingStrategy import ChainProcessingStrategy

class Chain(ChainBase):
    def __init__(self,
                 order_strategy: IChainOrderStrategy,
                 processing_strategy: ChainProcessingStrategy = ChainProcessingStrategy(),
                 steps: List[IChainStep] = None,
                 **configs):
        """
        Initializes a chain with an order and processing strategy, and optionally a list of steps.

        Args:
            order_strategy (IChainOrderStrategy): The strategy to order the chain steps.
            processing_strategy (ChainProcessingStrategy): The strategy to process the chain steps.
            steps (List[IChainStep]): Optional. Initial list of steps to be added to the chain.
            **configs: Additional configurations.
        """
        super().__init__(order_strategy, processing_strategy, steps, **configs)

    def execute(self) -> Any:
        """
        Executes the chain according to the defined steps, ordering strategy, and processing strategy,
        and returns the result of the execution.

        Returns:
            Any: The result of executing the chain steps.
        """
        ordered_steps = self.order_strategy.order_steps(self.steps)
        return self.processing_strategy.execute_steps(ordered_steps)
from typing import Literal
from swarmauri_base.chains.ChainStepBase import ChainStepBase

class ChainStep(ChainStepBase):
    """
    Represents a single step within an execution chain.
    """
    type: Literal['ChainStep'] = 'ChainStep'

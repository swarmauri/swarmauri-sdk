from typing import Literal
from swarmauri_base.chains.PromptContextChainBase import PromptContextChainBase

class PromptContextChain(PromptContextChainBase):
    type: Literal['PromptContextChain'] = 'PromptContextChain'
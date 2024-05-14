from typing import List, Dict, Any
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.prompts.IPromptMatrix import IPromptMatrix
from swarmauri.standard.chains.base.PromptStateChainBase import PromptStateChainBase

class PromptContextChain(PromptStateChainBase):
    def __init__(self, prompt_matrix: IPromptMatrix, 
        agents: List[IAgent] = [], context: Dict = {},
        model_kwargs: Dict[str, Any] = {}
        ):

        PromptStateChainBase.__init__(self, prompt_matrix=prompt_matrix, agents=agents, 
            context=context, model_kwargs=model_kwargs)

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Literal
from pydantic import Field
from collections import defaultdict, deque
import re
import numpy as np


from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.chains.ChainStepBase import ChainStepBase
from swarmauri_base.chains.ChainContextBase import ChainContextBase
from swarmauri_base.prompts.PromptMatrixBaseBase import PromptMatrixBase
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_core.prompts.IPromptMatrixBase import IPromptMatrixBase
from swarmauri_core.chains.IChainDependencyResolver import IChainDependencyResolver

class PromptContextChainBase(IChainDependencyResolver, ChainContextBase, ComponentBase):
    prompt_matrix: PromptMatrixBase
    agents: List[SubclassUnion[AgentBase]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    llm_kwargs: Dict[str, Any] = Field(default_factory=dict)
    response_matrix: Optional[PromptMatrixBase] = None
    current_step_index: int = 0
    steps: List[Any] = Field(default_factory=list)
    resource: Optional[str] =  Field(default=ResourceTypes.CHAIN.value)
    type: Literal['PromptContextChainBase'] = 'PromptContextChainBase'
    
    def __init__(self, **data: Any):
        super().__init__(**data)
        # Now that the instance is created, we can safely access `prompt_matrix.shape`
        self.response_matrix = PromptMatrixBase(matrix=[[None for _ in range(self.prompt_matrix.shape[1])] 
                                                    for _ in range(self.prompt_matrix.shape[0])])

    def execute(self, build_dependencies=True) -> None:
        """
        Execute the chain of prompts based on the state of the prompt matrix.
        Iterates through each sequence in the prompt matrix, resolves dependencies, 
        and executes prompts in the resolved order.
        """
        if build_dependencies:
            self.steps = self.build_dependencies()
            self.current_step_index = 0

        while self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            method = step.method
            args = step.args
            ref = step.ref
            result = method(*args)
            self.context[ref] = result
            prompt_index = self._extract_step_number(ref)
            self._update_response_matrix(args[0], prompt_index, result)
            self.current_step_index += 1  # Move to the next step
        else:
            print("All steps have been executed.")

    def execute_next_step(self):
        """
        Execute the next step in the steps list if available.
        """
        if self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            method = step.method
            args = step.args
            ref = step.ref
            result = method(*args)
            self.context[ref] = result
            prompt_index = self._extract_step_number(ref)
            self._update_response_matrix(args[0], prompt_index, result)
            self.current_step_index += 1  # Move to the next step
        else:
            print("All steps have been executed.")

    def _execute_prompt(self, agent_index: int, prompt: str, ref: str):
        """
        Executes a given prompt using the specified agent and updates the response.
        """
        formatted_prompt = prompt.format(**self.context)  # Using context for f-string formatting
        
        agent = self.agents[agent_index]
        # get the unformatted version
        unformatted_system_context = agent.system_context
        # use the formatted version
        agent.system_context = agent.system_context.content.format(**self.context)
        response = agent.exec(formatted_prompt, model_kwargs=self.model_kwargs)
        # reset back to the unformatted version
        agent.system_context = unformatted_system_context

        self.context[ref] = response
        prompt_index = self._extract_step_number(ref)
        self._update_response_matrix(agent_index, prompt_index, response)
        return response

    def _update_response_matrix(self, agent_index: int, prompt_index: int, response: Any):
        self.response_matrix.matrix[agent_index][prompt_index] = response


    def _extract_agent_number(self, text):
        # Regular expression to match the pattern and capture the agent number
        match = re.search(r'\{Agent_(\d+)_Step_\d+_response\}', text)
        if match:
            # Return the captured group, which is the agent number
            return int(match.group(1))
        else:
            # Return None if no match is found
            return None
    
    def _extract_step_number(self, ref):
        # This regex looks for the pattern '_Step_' followed by one or more digits.
        match = re.search(r"_Step_(\d+)_", ref)
        if match:
            return int(match.group(1))  # Convert the extracted digits to an integer
        else:
            return None  # If no match is found, return None
    
    def build_dependencies(self) -> List[ChainStepBase]:
        """
        Build the chain steps in the correct order by resolving dependencies first.
        """
        steps = []
        
        for i in range(self.prompt_matrix.shape[1]):
            try:
                sequence = np.array(self.prompt_matrix.matrix)[:,i].tolist()
                execution_order = self.resolve_dependencies(sequence=sequence)
                for j in execution_order:
                    prompt = sequence[j]
                    if prompt:
                        ref = f"Agent_{j}_Step_{i}_response"  # Using a unique reference string
                        step = ChainStepBase(
                            key=f"Agent_{j}_Step_{i}",
                            method=self._execute_prompt,
                            args=[j, prompt, ref],
                            ref=ref
                        )
                        steps.append(step)
            except Exception as e:
                print(str(e))
        return steps

    def resolve_dependencies(self, sequence: List[Optional[str]]) -> List[int]:
        """
        Resolve dependencies within a specific sequence of the prompt matrix.
        
        Args:
            matrix (List[List[Optional[str]]]): The prompt matrix.
            sequence_index (int): The index of the sequence to resolve dependencies for.

        Returns:
            List[int]: The execution order of the agents for the given sequence.
        """
        
        return [x for x in range(0, len(sequence), 1)]
# swarmauri/standard/chains/base/PromptContextChainBase.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from collections import defaultdict, deque
import re


from swarmauri.standard.chains.concrete.ChainStep import ChainStep
from swarmauri.standard.chains.base.ChainContextBase import ChainContextBase
from swarmauri.standard.prompts.concrete.PromptMatrix import PromptMatrix
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.prompts.IPromptMatrix import IPromptMatrix
from swarmauri.core.chains.IChainDependencyResolver import IChainDependencyResolver

class PromptContextChainBase(ChainContextBase, IChainDependencyResolver):
    def __init__(self, 
        prompt_matrix: IPromptMatrix, 
        agents: List[IAgent] = [], 
        context: Dict = {},
        model_kwargs: Dict[str, Any] = {}):
        ChainContextBase.__init__(self)
        self.prompt_matrix = prompt_matrix
        self.response_matrix = PromptMatrix(matrix=[[None for _ in range(prompt_matrix.shape[1])] for _ in range(prompt_matrix.shape[0])])
        self.agents = agents
        self.context = context 
        self.model_kwargs = model_kwargs

    @property
    def context(self) -> Dict[str, Any]:
        return self._context

    @context.setter
    def context(self, value: Dict[str, Any]) -> None:
        self._context = value

    def execute(self) -> None:
        """
        Execute the chain of prompts based on the state of the prompt matrix.
        Iterates through each sequence in the prompt matrix, resolves dependencies, 
        and executes prompts in the resolved order.
        """
        steps = self.build_dependencies()
        for step in steps:
            method = step.method
            args = step.args
            ref = step.ref
            result = method(*args)
            self.context[ref] = result
            prompt_index = self._extract_step_number(ref)
            self._update_response_matrix(args[0], prompt_index, result)

    def _execute_prompt(self, agent_index: int, prompt: str, ref: str):
        """
        Executes a given prompt using the specified agent and updates the response.
        """
        formatted_prompt = prompt.format(**self.context)  # Using context for f-string formatting
        agent = self.agents[agent_index]
        response = agent.exec(formatted_prompt, model_kwargs=self.model_kwargs)
        self.context[ref] = response
        prompt_index = self._extract_step_number(ref)
        self._update_response_matrix(agent_index, prompt_index, response)
        return response

    def _update_response_matrix(self, agent_index: int, prompt_index: int, response: Any):
        self.response_matrix.matrix[agent_index][prompt_index] = response


    def _extract_step_number(self, ref):
        # This regex looks for the pattern '_Step_' followed by one or more digits.
        match = re.search(r"_Step_(\d+)_", ref)
        if match:
            return int(match.group(1))  # Convert the extracted digits to an integer
        else:
            return None  # If no match is found, return None
    
    def build_dependencies(self) -> List[ChainStep]:
        """
        Build the chain steps in the correct order by resolving dependencies first.
        """
        steps = []
        for i, sequence in enumerate(self.prompt_matrix.matrix):
            execution_order = self.resolve_dependencies(matrix=self.prompt_matrix.matrix, sequence_index=i)
            for j in execution_order:
                prompt = sequence[j]
                if prompt:
                    ref = f"Agent_{i}_Step_{j}_response"  # Using a unique reference string
                    step = ChainStep(
                        key=f"Agent_{i}_Step_{j}",
                        method=self._execute_prompt,
                        args=[i, prompt, ref],
                        ref=ref
                    )
                    steps.append(step)
        return steps

    def resolve_dependencies(self, matrix: List[List[Optional[str]]], sequence_index: int) -> List[int]:
        """
        Resolve dependencies within a specific sequence of the prompt matrix.
        
        Args:
            matrix (List[List[Optional[str]]]): The prompt matrix.
            sequence_index (int): The index of the sequence to resolve dependencies for.

        Returns:
            List[int]: The execution order of the agents for the given sequence.
        """
        indegrees = defaultdict(int)
        graph = defaultdict(list)
        for agent_idx, prompt in enumerate(matrix[sequence_index]):
            if prompt:
                dependencies = re.findall(r'\$\d+_\d+', prompt)
                for dep in dependencies:
                    # Extract index from the matched dependency pattern "$x_y"
                    x = int(dep[1:])  # Remove leading "$" and convert to int
                    graph[x].append(agent_idx)
                    indegrees[agent_idx] += 1
                if not dependencies:
                    indegrees[agent_idx] = 0
            else:
                indegrees[agent_idx] = 0  # Ensure nodes without dependencies are in the graph
        
        queue = deque([idx for idx in indegrees if indegrees[idx] == 0])
        execution_order = []
        while queue:
            current = queue.popleft()
            execution_order.append(current)
            for dependent in graph[current]:
                indegrees[dependent] -= 1
                if indegrees[dependent] == 0:
                    queue.append(dependent)
        if len(execution_order) != len(indegrees):
            raise RuntimeError("There's a cyclic dependency or unresolved dependency in your prompt matrix.")
        return execution_order


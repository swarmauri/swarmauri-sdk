# File: swarmauri/workflows/node.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
from swarmauri_workflow_statedriven.input_modes.base import InputMode
from swarmauri_workflow_statedriven.input_modes.first import FirstInputMode
from swarmauri_workflow_statedriven.join_strategies.base import JoinStrategy
from swarmauri_workflow_statedriven.join_strategies.first_join import FirstJoinStrategy
from swarmauri_workflow_statedriven.merge_strategies.base import MergeStrategy
from swarmauri_workflow_statedriven.merge_strategies.list_merge import ListMergeStrategy
from swarmauri_workflow_statedriven.state_manager import StateManager
from swarmauri_workflow_statedriven.exceptions import WorkflowError


class Node:
    """
    File: workflows/node.py
    Class: Node
    Methods:
      - __init__: initialize name, agent/tool, input_mode, join & merge strategies
      - prepare_input: apply InputMode.prepare
      - execute: run the agent.exec or tool.run on a scalar
      - batch: run agent.batch/tool.batch or fallback to execute-per-item
      - run: orchestrate prepare_input + execute()/batch()
      - validate: sanity‑check output (default always True)
    """

    def __init__(
        self,
        name: str,
        agent: Optional[Any] = None,
        tool: Optional[Any] = None,
        input_mode: "InputMode" = None,
        join_strategy: "JoinStrategy" = None,
        merge_strategy: "MergeStrategy" = None,
    ):
        """
        File: workflows/node.py
        Class: Node
        Method: __init__

        Args:
            name: unique identifier
            agent: Agent with exec(input)->output
            tool: Tool with run(input)->output
            input_mode: strategy for shaping raw data
            join_strategy: strategy for gating multi-branch joins
            merge_strategy: strategy for combining buffered inputs
        Raises:
            ValueError if neither or both of agent/tool are provided.
        """
        if (agent is None) == (tool is None):
            raise ValueError(f"Node '{name}' requires exactly one of agent or tool")

        self.name = name
        self.agent = agent
        self.tool = tool
        self.input_mode = input_mode or FirstInputMode()
        self.join_strategy = join_strategy or FirstJoinStrategy()
        self.merge_strategy = merge_strategy or ListMergeStrategy()

    def prepare_input(
        self, state_manager: "StateManager", data: Any, results: Dict[str, Any]
    ) -> Any:
        """
        File: workflows/node.py
        Class: Node
        Method: prepare_input

        Apply the node's InputMode to shape the incoming data.
        """
        return self.input_mode.prepare(state_manager, self.name, data, results)

    def execute(self, input_data: Any) -> Any:
        """
        File: workflows/node.py
        Class: Node
        Method: execute

        Executes a single‐item call on agent.exec or tool.run.
        """
        if self.agent:
            if isinstance(input_data, (dict, list)):
                try:
                    input_data = json.dumps(input_data)
                    res = self.agent.exec(input_data)
                    print(res)
                    return res
                except Exception:
                    res = self.agent.exec(input_data)
                    print(res)
                    return res
            else:
                res = self.agent.exec(input_data)
                print(res)
                return res
        if self.tool:
            res = self.tool.call(input_data)
            print(res)
            return res
        raise WorkflowError(f"No execution backend for node '{self.name}'")

    def batch(self, inputs: List[Any]) -> Any:
        """
        File: workflows/node.py
        Class: Node
        Method: batch

        Executes a batch call on agent.batch or tool.batch if present,
        otherwise falls back to per‐item execute().
        """
        if self.agent and hasattr(self.agent, "batch"):
            res = self.agent.batch(inputs)
            print(res)
            return res
        if self.tool and hasattr(self.tool, "batch"):
            res = self.tool.batch(inputs)
            print(res)
            return res
        res = [self.execute(item) for item in inputs]
        print(res)
        return res

    def run(
        self, state_manager: "StateManager", data: Any, results: Dict[str, Any]
    ) -> Any:
        """
        File: workflows/node.py
        Class: Node
        Method: run

        Full node invocation:
          1. prepare_input
          2. if prepare_input returned None, skip execution (e.g. split mode)
          3. dispatch to batch() if list, else execute()
        """
        prepared = self.prepare_input(state_manager, data, results)
        if prepared is None:
            return None
        if isinstance(prepared, list):
            return self.batch(prepared)
        return self.execute(prepared)

    def validate(self, output: Any) -> bool:
        """
        File: workflows/node.py
        Class: Node
        Method: validate

        Default validation always returns True. Override or wrap with Condition.
        """
        return True

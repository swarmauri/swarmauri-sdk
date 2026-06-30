# File: swarmauri/workflows/base.py

import threading
from typing import Any, Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, FIRST_COMPLETED, wait

from swarmauri_workflow_statedriven.node import Node
from swarmauri_workflow_statedriven.transition import Transition
from swarmauri_workflow_statedriven.state_manager import StateManager
from swarmauri_workflow_statedriven.exceptions import InvalidTransitionError
from swarmauri_workflow_statedriven.conditions.base import Condition
from swarmauri_workflow_statedriven.join_strategies.base import JoinStrategy
from swarmauri_workflow_statedriven.merge_strategies.base import MergeStrategy


class WorkflowBase:
    """
    File: workflows/base.py
    Class: WorkflowBase
    """

    def __init__(self):
        """
        Method: __init__
        Initialize nodes, transitions, state_manager, and a lock for thread safety.
        """
        self.nodes: Dict[str, Node] = {}
        self.transitions: List[Transition] = []
        self.state_manager = StateManager()
        self._lock = threading.Lock()

    def add_state(
        self,
        name: str,
        *,
        agent: Optional[Any] = None,
        tool: Optional[Any] = None,
        input_mode: Any = None,
        join_strategy: Optional[JoinStrategy] = None,
        merge_strategy: Optional[MergeStrategy] = None,
    ) -> None:
        """
        Method: add_state
        Registers a Node with its execution backend, input_mode, join and merge strategies.
        """
        node = Node(
            name=name,
            agent=agent,
            tool=tool,
            input_mode=input_mode,
            join_strategy=join_strategy,
            merge_strategy=merge_strategy,
        )
        self.nodes[name] = node

    def add_transition(self, source: str, target: str, condition: Condition) -> None:
        """
        Method: add_transition
        Registers a guarded, directed edge between two existing states.
        """
        if source not in self.nodes or target not in self.nodes:
            raise InvalidTransitionError(
                f"Cannot add transition: '{source}' → '{target}'"
            )
        self.transitions.append(Transition(source, target, condition))

    def run(self, start: str, initial_input: Any) -> Dict[str, Any]:
        """
        Method: run
        Single‐threaded execution loop.
        """
        if start not in self.nodes:
            raise InvalidTransitionError(f"Start state '{start}' is not defined")

        results: Dict[str, Any] = {}
        queue: List[Tuple[str, Any]] = [(start, initial_input)]

        while queue:
            state_name, data = queue.pop(0)
            node = self.nodes[state_name]

            # ① Run the node (handles input_mode, split, merge, batch internally)
            print(
                f"[DEBUG] Running {node.name} with \n\tdata: {data}\n\tresults: {results}"
            )
            output = node.run(self.state_manager, data, results)

            # ② If split mode returned None, that work was re-enqueued
            if output is None:
                continue

            # ③ Record result
            results[state_name] = output
            with self._lock:
                self.state_manager.update_state(state_name, output)

            # ④ Propagate through transitions
            for t in self.transitions:
                if t.source != state_name or not t.condition.evaluate(results):
                    continue

                with self._lock:
                    self.state_manager.buffer_input(t.target, output)

                buffer = self.state_manager.get_buffer(t.target)
                if self.nodes[t.target].join_strategy.is_satisfied(buffer):
                    raw = self.state_manager.pop_buffer(t.target)
                    merged = self.nodes[t.target].merge_strategy.merge(raw)
                    queue.append((t.target, merged))

        return results

    def run_parallel(
        self, start: str, initial_input: Any, max_workers: int = None
    ) -> Dict[str, Any]:
        """
        Method: run_parallel
        Executes ready‐to‐run node invocations in parallel threads.
        """
        if start not in self.nodes:
            raise InvalidTransitionError(f"Start state '{start}' is not defined")

        results: Dict[str, Any] = {}
        executor = ThreadPoolExecutor(max_workers=max_workers)
        futures = []

        def _run_node(name: str, payload: Any) -> Tuple[str, Any]:
            node = self.nodes[name]
            return name, node.run(self.state_manager, payload, results)

        # Seed with the start state
        futures.append(executor.submit(_run_node, start, initial_input))

        while futures:
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for fut in done:
                state_name, output = fut.result()
                futures.remove(fut)

                # If split, skip recording & scheduling (node.run already re-queued)
                if output is None:
                    continue

                # Record under lock
                with self._lock:
                    results[state_name] = output
                    self.state_manager.update_state(state_name, output)

                # Schedule downstream work
                for t in self.transitions:
                    if t.source != state_name or not t.condition.evaluate(results):
                        continue

                    with self._lock:
                        self.state_manager.buffer_input(t.target, output)

                    buffer = self.state_manager.get_buffer(t.target)
                    if self.nodes[t.target].join_strategy.is_satisfied(buffer):
                        raw = self.state_manager.pop_buffer(t.target)
                        merged = self.nodes[t.target].merge_strategy.merge(raw)
                        futures.append(executor.submit(_run_node, t.target, merged))

        executor.shutdown(wait=True)
        return results

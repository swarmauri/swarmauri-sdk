"""Checkpoint the existing guarded workflow one node at a time."""

import asyncio
import copy
import inspect
import json
from typing import Any, Callable, Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.executions import ExecutionDriverBase
from swarmauri_core.executions import DriverStep, ExecutionCapabilities
from .state_manager import StateManager


@ComponentBase.register_type(ExecutionDriverBase, "StateDrivenExecutionDriver")
class StateDrivenExecutionDriver(ExecutionDriverBase):
    """Reuse conditions, joins and merges with durable scheduling state.

    The host versions definitions and injects an authorized dispatcher for
    remote nodes. Strategy state must be JSON serializable; subclasses may
    override dump_strategy/restore_strategy for custom strategies.
    """

    type: Literal["StateDrivenExecutionDriver"] = "StateDrivenExecutionDriver"
    graph: Any = Field(exclude=True, repr=False)
    definition_version: str
    dispatcher: Callable | None = Field(default=None, exclude=True, repr=False)

    def supports(self):
        return ExecutionCapabilities()

    def dump_strategy(self, strategy):
        return json.loads(json.dumps(vars(strategy)))

    def restore_strategy(self, strategy, state):
        strategy.__dict__.update(state)

    async def step(self, snapshot):
        state = copy.deepcopy(snapshot.state)
        version = state.setdefault("definition_version", self.definition_version)
        if version != self.definition_version:
            raise ValueError("Workflow definition version changed")
        queue = state.setdefault("queue", [[state["start"], state.get("input")]])
        results = state.setdefault("results", {})
        buffers = state.setdefault("buffers", {})
        strategies = state.setdefault("strategies", {})
        if not queue:
            return DriverStep(state, completed=True, result=results)
        manager = StateManager()
        manager.state = dict(results)
        manager.join_buffers = buffers
        nodes = {}
        for name, template in self.graph.nodes.items():
            node = copy.copy(template)
            for attribute in ("input_mode", "join_strategy", "merge_strategy"):
                strategy = copy.deepcopy(getattr(template, attribute))
                saved = strategies.get(name, {}).get(attribute)
                if saved is not None:
                    self.restore_strategy(strategy, saved)
                elif attribute == "join_strategy" and hasattr(strategy, "configure"):
                    strategy.configure(
                        sum(t.target == name for t in self.graph.transitions)
                    )
                setattr(node, attribute, strategy)
            nodes[name] = node
        name, data = queue.pop(0)
        node = nodes[name]
        if self.dispatcher is None:
            output = await asyncio.to_thread(node.run, manager, data, results)
        else:
            prepared = node.prepare_input(manager, data, results)
            output = self.dispatcher(name, prepared, snapshot)
            if inspect.isawaitable(output):
                output = await output
        if output is not None:
            results[name] = output
            manager.update_state(name, output)
            for transition in self.graph.transitions:
                if transition.source != name or not transition.is_triggered(results):
                    continue
                target = nodes[transition.target]
                manager.buffer_input(transition.target, output)
                target.join_strategy.mark_complete(name)
                buffer = manager.get_buffer(transition.target)
                if target.join_strategy.is_satisfied(buffer):
                    raw = manager.pop_buffer(transition.target)
                    queue.append([transition.target, target.merge_strategy.merge(raw)])
                    target.join_strategy.reset()
        state["buffers"] = manager.join_buffers
        state["strategies"] = {
            name: {
                attribute: self.dump_strategy(getattr(node, attribute))
                for attribute in ("input_mode", "join_strategy", "merge_strategy")
            }
            for name, node in nodes.items()
        }
        # Fail before checkpointing unsupported outputs or strategy state.
        json.dumps(state)
        return DriverStep(state, completed=not queue, result=dict(results))

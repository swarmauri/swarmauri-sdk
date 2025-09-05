from typing import Any, List, Literal, Type

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.swarms.SwarmBase import SwarmBase


@ComponentBase.register_type(SwarmBase, "Swarm")
class Swarm(SwarmBase):
    """Concrete implementation of SwarmBase for task processing"""

    type: Literal["Swarm"] = "Swarm"
    agent_class: Type[Any] = Field(description="Agent class to use for swarm")
    agents: List[SubclassUnion["AgentBase"]] = []

    def _create_agent(self) -> Any:
        """Create new agent instance"""
        return self.agent_class()

from typing import Any, Dict, List, Literal, Optional, Type, Union
from pydantic import Field

from swarmauri_base.swarms.SwarmBase import SwarmBase, SwarmStatus
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(SwarmBase, "Swarm")
class Swarm(SwarmBase):
    """Concrete implementation of SwarmBase for task processing"""

    type: Literal["Swarm"] = "Swarm"
    agent_class: Type[Any] = Field(description="Agent class to use for swarm")
    agents: List[SubClassUnion["AgentBase"]] = []

    def _create_agent(self) -> Any:
        """Create new agent instance"""
        return self.agent_class()


from typing import Any, Dict, Literal, Optional

from pydantic import ConfigDict, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.agent_apis.IAgentAPI import IAgentAPI
from swarmauri.service_registries.concrete.ServiceRegistry import ServiceRegistry


class AgentAPIBase(IAgentAPI, ComponentBase):

    resource: Optional[str] = Field(default=ResourceTypes.AGENT_API.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["AgentAPIBase"] = "AgentAPIBase"

    agent_registry: ServiceRegistry

    def invoke(self, agent_id: str, **kwargs: Dict[str, Any]) -> Any:
        agent = self.agent_registry.get_service(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found.")
        return agent.exec(**kwargs)

    async def ainvoke(self, agent_id: str, **kwargs: Dict[str, Any]) -> Any:
        agent = self.agent_registry.get_service(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID {agent_id} not found.")
        if not hasattr(agent, "aexec"):
            raise NotImplementedError(
                f"Agent with ID {agent_id} does not support async execution."
            )
        return await agent.aexec(**kwargs)

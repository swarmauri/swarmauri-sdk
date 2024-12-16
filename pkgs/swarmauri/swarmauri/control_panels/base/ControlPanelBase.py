from swarmauri_core.control_panels.IControlPanel import IControlPlane
from typing import Any, List, Literal
from pydantic import Field, ConfigDict
from swarmauri_core.ComponentBase import ResourceTypes
from swarmauri.service_registries.base.ServiceRegistryBase import ServiceRegistryBase
from swarmauri.factories.base.FactoryBase import FactoryBase
from swarmauri.task_mgt_strategies.base.TaskMgtStrategyBase import TaskMgtStrategyBase
from swarmauri.transports.base.TransportBase import TransportBase
from swarmauri_core.typing import SubclassUnion


class ControlPanelBase(IControlPlane):
    """
    Implementation of the ControlPlane abstract class.
    """

    resource: ResourceTypes = Field(default=ResourceTypes.CONTROL_PANEL.value)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["ControlPanelBase"] = "ControlPanelBase"

    agent_factory: SubclassUnion[FactoryBase]
    service_registry: SubclassUnion[ServiceRegistryBase]
    task_mgt_strategy: SubclassUnion[TaskMgtStrategyBase]
    transport: SubclassUnion[TransportBase]

    def create_agent(self, name: str, role: str) -> Any:
        """
        Create an agent with the given name and role.
        """
        agent = self.agent_factory.create_agent(name, role)
        self.service_registry.register_service(name, {"role": role, "status": "active"})
        return agent

    def distribute_tasks(self, task: Any) -> None:
        """
        Distribute tasks using the task strategy.
        """
        self.task_mgt_strategy.assign_task(task, self.service_registry)

    def orchestrate_agents(self, task: Any) -> None:
        """
        Orchestrate agents for task distribution.
        """
        self.distribute_tasks(task)

    def remove_agent(self, name: str) -> None:
        """
        Remove the agent with the specified name.
        """
        agent = self.agent_factory.get_agent_by_name(name)
        if not agent:
            raise ValueError(f"Agent {name} not found.")
        self.service_registry.unregister_service(name)
        self.agent_factory.delete_agent(name)

    def list_active_agents(self) -> List[str]:
        """
        List all active agent names.
        """
        agents = self.agent_factory.get_agents()
        return [agent.name for agent in agents if agent]

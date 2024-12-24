from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.control_panels.IControlPanel import IControlPlane
from typing import Any, List, Literal
from pydantic import Field, ConfigDict
from swarmauri_base.service_registries.ServiceRegistryBase import ServiceRegistryBase
from swarmauri_base.factories.FactoryBase import FactoryBase
from swarmauri_base.task_mgt_strategies.TaskMgtStrategyBase import TaskMgtStrategyBase
from swarmauri_base.transports.TransportBase import TransportBase
from swarmauri_core.typing import SubclassUnion
import logging


class ControlPanelBase(IControlPlane, ComponentBase):
    """
    Implementation of the ControlPlane abstract class.
    This class orchestrates agents, manages tasks, and ensures task distribution
    and transport between agents and services.
    """

    resource: ResourceTypes = Field(default=ResourceTypes.CONTROL_PANEL.value)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["ControlPanelBase"] = "ControlPanelBase"

    agent_factory: SubclassUnion[FactoryBase]
    service_registry: SubclassUnion[ServiceRegistryBase]
    task_mgt_strategy: SubclassUnion[TaskMgtStrategyBase]
    transport: SubclassUnion[TransportBase]

    # Agent management methods
    def create_agent(self, name: str, role: str) -> Any:
        """
        Create an agent with the given name and role, and register it in the service registry.
        """
        agent = self.agent_factory.create_agent(name, role)
        self.service_registry.register_service(name, {"role": role, "status": "active"})
        logging.info(f"Agent '{name}' with role '{role}' created and registered.")
        return agent

    def remove_agent(self, name: str) -> None:
        """
        Remove the agent with the specified name and unregister it from the service registry.
        """
        agent = self.agent_factory.get_agent_by_name(name)
        if not agent:
            raise ValueError(f"Agent '{name}' not found.")
        self.service_registry.unregister_service(name)
        self.agent_factory.delete_agent(name)
        logging.info(f"Agent '{name}' removed and unregistered.")

    def list_active_agents(self) -> List[str]:
        """
        List all active agent names.
        """
        agents = self.agent_factory.get_agents()
        active_agents = [agent.name for agent in agents if agent]
        logging.info(f"Active agents listed: {active_agents}")
        return active_agents

    # Task management methods
    def submit_tasks(self, tasks: List[Any]) -> None:
        """
        Submit one or more tasks to the task management strategy for processing.
        """
        for task in tasks:
            self.task_mgt_strategy.add_task(task)
            logging.info(
                f"Task '{task.get('task_id', 'unknown')}' submitted to the strategy."
            )

    def process_tasks(self) -> None:
        """
        Process and assign tasks from the queue, then transport them to their assigned services.
        """
        try:
            self.task_mgt_strategy.process_tasks(
                self.service_registry.get_services, self.transport
            )
            logging.info("Tasks processed and transported successfully.")
        except Exception as e:
            logging.error(f"Error while processing tasks: {e}")
            raise ValueError(f"Error processing tasks: {e}")

    def distribute_tasks(self, task: Any) -> None:
        """
        Distribute tasks using the task strategy (manual or on-demand assignment).
        """
        self.task_mgt_strategy.assign_task(task, self.service_registry.get_services)
        logging.info(
            f"Task '{task.get('task_id', 'unknown')}' distributed to a service."
        )

    # Orchestration method
    def orchestrate_agents(self, tasks: List[Any]) -> None:
        """
        Orchestrate agents for task distribution and transportation.
        """
        self.submit_tasks(tasks)  # Add task to the strategy
        self.process_tasks()  # Process and transport the task
        logging.info("Agents orchestrated successfully.")

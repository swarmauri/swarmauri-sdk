import logging
from typing import List, Any, Dict, Literal
from swarmauri import task_mgt_strategies
from swarmauri.factories.base.FactoryBase import FactoryBase
from swarmauri.mas.base.MasBase import MasBase
from swarmauri.transports.base.TransportBase import TransportBase
from swarmauri.service_registries.concrete import ServiceRegistry
from swarmauri.task_mgt_strategies.base.TaskMgtStrategyBase import TaskMgtStrategyBase
from swarmauri.control_panels.concrete.ControlPanel import ControlPanel
from swarmauri_core.typing import SubclassUnion


class CentralizedMas(MasBase):
    """Concrete implementation of the MasBase class."""

    transport: SubclassUnion[TransportBase]
    agent_factory: SubclassUnion[FactoryBase]
    service_registry: ServiceRegistry = ServiceRegistry()
    task_mgt_strategy: SubclassUnion[TaskMgtStrategyBase]
    control_panel: ControlPanel
    type: Literal["CentralizedMas"] = "CentralizedMas"

    def add_agent(self, name: str, role: Any, **kwarg: Any) -> None:
        if name in self.agent_factory.get():
            raise ValueError(f"Agent '{name}' already exists.")

        self.agent_factory.register(name, role)
        self.control_panel.create_agent(name, role, **kwarg)

    def remove_agent(self, name: str) -> None:
        if name in self.agent_factory.get():
            self.control_panel.remove_agent(name)

    def broadcast(self, message: Any) -> None:
        agents = self.agent_factory.get()
        self.transport.broadcast(message, agents)

    def multicast(self, message: Any, recipient_names: List[str]) -> None:
        recipients = [
            name
            for name in recipient_names
            if name in self.control_panel.list_active_agents().keys()
        ]
        self.transport.multicast(sender=self, message=message, recipients=recipients)

    def unicast(self, message: Any, recipient_name: str) -> None:
        if recipient_name in self.control_panel.list_active_agents().keys():
            self.transport.send(sender=self, message=message, recipient=recipient_name)

    def dispatch_task(self, task: Any, agent_id: str) -> None:
        if agent_id in self.control_panel.list_active_agents().keys():
            self.control_panel.distribute_tasks(task)

    def dispatch_tasks(self, tasks: List[Any], agent_ids: List[str]) -> None:
        for task, agent_id in zip(tasks, agent_ids):
            self.dispatch_task(task, agent_id)

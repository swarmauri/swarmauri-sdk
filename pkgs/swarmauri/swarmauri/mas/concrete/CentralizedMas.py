from typing import List, Any, Dict
from swarmauri.factories.base.FactoryBase import FactoryBase
from swarmauri.mas.base.MasBase import MasBase
from swarmauri.transport.base.TransportBase import TransportBase
from swarmauri.service_registries.concrete import ServiceRegistry
from swarmauri.task_mgt_strategies.base.TaskMgtStrategyBase import TaskMgtStrategyBase
from swarmauri.control_panels.concrete.ControlPanel import ControlPanel
from swarmauri_core.typing import SubclassUnion


class CentralizedMas(MasBase):
    """Concrete implementation of the MasBase class."""

    _agents: Dict[str, Any] = {}
    transport: SubclassUnion[TransportBase]
    factory: SubclassUnion[FactoryBase]
    service_registry: ServiceRegistry = ServiceRegistry()
    task_strategy: SubclassUnion[TaskMgtStrategyBase]
    control_panel: ControlPanel

    def __init__(self, transport: SubclassUnion[TransportBase], factory: SubclassUnion[FactoryBase], task_strategy: SubclassUnion[TaskMgtStrategyBase]):
        super().__init__()
        self._agents: Dict[str, Any] = {}
        self.transport = transport
        self.agent_factory = factory
        self.service_registry = ServiceRegistry()
        self.task_strategy = task_strategy
        self.control_plane = ControlPanel(
            self.agent_factory,
            self.service_registry,
            self.task_strategy,
            self.transport,
        )

    def add_agent(self, name: str, role: Any) -> None:
        agent = self.control_plane.create_agent(name, role)
        self._agents[name] = agent

    def remove_agent(self, name: str) -> None:
        if name in self._agents:
            self.control_plane.remove_agent(name)
            del self._agents[name]

    def broadcast(self, message: Any) -> None:
        agents = list(self._agents.values())
        self.transport.broadcast(message, agents)

    def multicast(self, message: Any, recipient_ids: List[str]) -> None:
        recipients = [
            self._agents[agent_id]
            for agent_id in recipient_ids
            if agent_id in self._agents
        ]
        self.transport.multicast(message, recipients)

    def unicast(self, message: Any, recipient_id: str) -> None:
        if recipient_id in self._agents:
            self.transport.send_message(message, self._agents[recipient_id])

    def dispatch_task(self, task: Any, agent_id: str) -> None:
        if agent_id in self._agents:
            self._agents[agent_id].perform_task(task)

    def dispatch_tasks(self, tasks: List[Any], agent_ids: List[str]) -> None:
        for task, agent_id in zip(tasks, agent_ids):
            self.dispatch_task(task, agent_id)

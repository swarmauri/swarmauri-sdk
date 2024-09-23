import importlib
from datetime import datetime
import json
from typing import Callable, Dict, Type, Any
from swarmauri_core.agents.IAgent import IAgent  # Update this import path as needed
from swarmauri_core.agentfactories.IAgentFactory import IAgentFactory
from swarmauri_core.agentfactories.IExportConf import IExportConf

class ReflectiveAgentFactory(IAgentFactory, IExportConf):
    def __init__(self):
        self._registry: Dict[str, Type[IAgent]] = {}
        self._metadata = {
            'id': None,
            'name': 'ReflectiveAgentFactory',
            'type': 'Reflective',
            'date_created': datetime.now(),
            'last_modified': datetime.now()
        }

    def create_agent(self, agent_type: str, **kwargs) -> IAgent:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        agent_class = self._registry[agent_type]
        return agent_class(**kwargs)

    def register_agent(self, agent_type: str, class_path: str) -> None:
        module_name, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        self._registry[agent_type] = cls
        self._metadata['last_modified'] = datetime.now()

    # Implementations for the IExportConf interface
    def to_dict(self) -> Dict[str, Any]:
        return self._metadata.copy()

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        with open(file_path, 'w') as file:
            file.write(self.to_json())

    # Property implementations: id, name, type, date_created, and last_modified
    @property
    def id(self) -> int:
        return self._metadata['id']

    @id.setter
    def id(self, value: int) -> None:
        self._metadata['id'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def name(self) -> str:
        return self._metadata['name']

    @name.setter
    def name(self, value: str) -> None:
        self._metadata['name'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def type(self) -> str:
        return self._metadata['type']

    @type.setter
    def type(self, value: str) -> None:
        self._metadata['type'] = value
        self._metadata['last_modified'] = datetime.now()

    @property
    def date_created(self) -> datetime:
        return self._metadata['date_created']

    @property
    def last_modified(self) -> datetime:
        return self._metadata['last_modified']

    @last_modified.setter
    def last_modified(self, value: datetime) -> None:
        self._metadata['last_modified'] = value
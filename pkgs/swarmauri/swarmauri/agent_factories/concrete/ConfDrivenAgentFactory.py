import json
import importlib
from datetime import datetime
from typing import Any, Dict, Callable
from swarmauri_core.agents.IAgent import IAgent  # Replace with the correct IAgent path
from swarmauri_core.agentfactories.IAgentFactory import IAgentFactory
from swarmauri_core.agentfactories.IExportConf import IExportConf


class ConfDrivenAgentFactory(IAgentFactory, IExportConf):
    def __init__(self, config_path: str):
        self._config_path = config_path
        self._config = self._load_config(config_path)
        self._registry = {}
        self._metadata = {
            'id': None,
            'name': 'ConfAgentFactory',
            'type': 'Configurable',
            'date_created': datetime.now(),
            'last_modified': datetime.now()
        }
        
        self._initialize_registry()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as file:
            return json.load(file)
    
    def _initialize_registry(self) -> None:
        for agent_type, agent_info in self._config.get("agents", {}).items():
            module_name, class_name = agent_info["class_path"].rsplit('.', 1)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            self.register_agent(agent_type, cls)
    
    # Implementation of IAgentFactory methods
    def create_agent(self, agent_type: str, **kwargs) -> IAgent:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        return self._registry[agent_type](**kwargs)

    def register_agent(self, agent_type: str, constructor: Callable[..., IAgent]) -> None:
        self._registry[agent_type] = constructor
        self._metadata['last_modified'] = datetime.now()
    
    # Implementation of IExportConf methods
    def to_dict(self) -> Dict[str, Any]:
        return self._metadata.copy()

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        with open(file_path, 'w') as f:
            f.write(self.to_json())

    # Additional methods to implement required properties and their setters
    # Implementing getters and setters for metadata properties as needed
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
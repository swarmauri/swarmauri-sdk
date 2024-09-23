import json
from datetime import datetime
from typing import Callable, Dict, Any
from swarmauri_core.agents.IAgent import IAgent
from swarmauri_core.agent_factories.IAgentFactory import IAgentFactory
from swarmauri_core.agent_factories.IExportConf import IExportConf


class AgentFactory(IAgentFactory, IExportConf):
    def __init__(self):
        """Initializes the AgentFactory with an empty registry and metadata."""
        self._registry: Dict[str, Callable[..., IAgent]] = {}
        self._metadata = {
            "id": None,
            "name": "DefaultAgentFactory",
            "type": "Generic",
            "date_created": datetime.now(),
            "last_modified": datetime.now(),
        }

    # Implementation of IAgentFactory methods
    def create_agent(self, agent_type: str, **kwargs) -> IAgent:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")

        constructor = self._registry[agent_type]
        return constructor(**kwargs)

    def register_agent(
        self, agent_type: str, constructor: Callable[..., IAgent]
    ) -> None:
        if agent_type in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is already registered.")
        self._registry[agent_type] = constructor
        self._metadata["last_modified"] = datetime.now()

    # Implementation of IExportConf methods
    def to_dict(self) -> Dict[str, Any]:
        """Exports the registry metadata as a dictionary."""
        export_data = self._metadata.copy()
        export_data["registry"] = list(self._registry.keys())
        return export_data

    def to_json(self) -> str:
        """Exports the registry metadata as a JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        """Exports the registry metadata to a file."""
        with open(file_path, "w") as f:
            f.write(self.to_json())

    @property
    def id(self) -> int:
        return self._metadata["id"]

    @id.setter
    def id(self, value: int) -> None:
        self._metadata["id"] = value
        self._metadata["last_modified"] = datetime.now()

    @property
    def name(self) -> str:
        return self._metadata["name"]

    @name.setter
    def name(self, value: str) -> None:
        self._metadata["name"] = value
        self._metadata["last_modified"] = datetime.now()

    @property
    def type(self) -> str:
        return self._metadata["type"]

    @type.setter
    def type(self, value: str) -> None:
        self._metadata["type"] = value
        self._metadata["last_modified"] = datetime.now()

    @property
    def date_created(self) -> datetime:
        return self._metadata["date_created"]

    @property
    def last_modified(self) -> datetime:
        return self._metadata["last_modified"]

    @last_modified.setter
    def last_modified(self, value: datetime) -> None:
        self._metadata["last_modified"] = value

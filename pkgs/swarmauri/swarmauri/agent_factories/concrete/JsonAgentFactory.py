import json
from jsonschema import validate, ValidationError
from typing import Dict, Any, Callable, Type
from swarmauri_core.agents.IAgent import IAgent
from swarmauri_core.agent_factories.IAgentFactory import IAgentFactory
from swarmauri_core.agent_factories.IExportConf import IExportConf
import importlib

class JsonAgentFactory:
    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._registry: Dict[str, Type[Any]] = {}

        # Load and validate config
        self._validate_config()
        self._load_config()

    def _validate_config(self) -> None:
        """Validates the configuration against the JSON schema."""
        schema = {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "agents": {
                  "type": "object",
                  "patternProperties": {
                    "^[a-zA-Z][a-zA-Z0-9_-]*$": {
                      "type": "object",
                      "properties": {
                        "constructor": {
                          "type": "object",
                          "required": ["module", "class"]
                        }
                      },
                      "required": ["constructor"]
                    }
                  }
                }
              },
              "required": ["agents"]
            }

        try:
            validate(instance=self._config, schema=schema)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e.message}")

    def _load_config(self):
        """Loads configuration and registers agents accordingly."""
        agents_config = self._config.get("agents", {})
        for agent_type, agent_info in agents_config.items():
            module_name = agent_info["constructor"]["module"]
            class_name = agent_info["constructor"]["class"]

            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)

            self.register_agent(agent_type, cls)

    def create_agent(self, agent_type: str, **kwargs) -> Any:
        if agent_type not in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is not registered.")
        
        constructor = self._registry[agent_type]
        print(f"Creating instance of {constructor}, with args: {kwargs}")
        return constructor(**kwargs)

    def register_agent(self, agent_type: str, constructor: Callable[..., Any]) -> None:
        if agent_type in self._registry:
            raise ValueError(f"Agent type '{agent_type}' is already registered.")
        
        print(f"Registering agent type '{agent_type}' with constructor: {constructor}")
        self._registry[agent_type] = constructor

    def to_dict(self) -> Dict[str, Any]:
        return self._config

    def to_json(self) -> str:
        return json.dumps(self._config, default=str, indent=4)

    def export_to_file(self, file_path: str) -> None:
        with open(file_path, 'w') as file:
            file.write(self.to_json())

    @property
    def id(self) -> int:
        return self._config.get('id', None)  # Assuming config has an 'id'.

    @id.setter
    def id(self, value: int) -> None:
        self._config['id'] = value

    @property
    def name(self) -> str:
        return self._config.get('name', 'ConfDrivenAgentFactory')

    @name.setter
    def name(self, value: str) -> None:
        self._config['name'] = value

    @property
    def type(self) -> str:
        return self._config.get('type', 'Configuration-Driven')

    @type.setter
    def type(self, value: str) -> None:
        self._config['type'] = value

    @property
    def date_created(self) -> str:
        return self._config.get('date_created', None)

    @property
    def last_modified(self) -> str:
        return self._config.get('last_modified', None)

    @last_modified.setter
    def last_modified(self, value: str) -> None:
        self._config['last_modified'] = value
        self._config['last_modified'] = value
from typing import Dict
from abc import ABC, abstractmethod
from swarmauri_core.tools.ITool import ITool

class IToolkit(ABC):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    @abstractmethod
    def add_tools(self, tools: Dict[str, ITool]):
        """
        An abstract method that should be implemented by subclasses to add multiple tools to the toolkit.
        """
        pass

    @abstractmethod
    def add_tool(self, tool: ITool):
        """
        An abstract method that should be implemented by subclasses to add a single tool to the toolkit.
        """
        pass

    @abstractmethod
    def remove_tool(self, tool_name: str):
        """
        An abstract method that should be implemented by subclasses to remove a tool from the toolkit by name.
        """
        pass

    @abstractmethod
    def get_tool_by_name(self, tool_name: str) -> ITool:
        """
        An abstract method that should be implemented by subclasses to retrieve a tool from the toolkit by name.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """
        An abstract method that should be implemented by subclasses to return the number of tools in the toolkit.
        """
        pass
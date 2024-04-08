from abc import ABC, abstractmethod
from typing import Dict
from ....core.toolkits.IToolkit import IToolkit
from ....core.tools.ITool import ITool  

class ToolkitBase(IToolkit, ABC):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    @abstractmethod
    def __init__(self, initial_tools: Dict[str, ITool] = None):
        """
        Initialize the Toolkit with an optional dictionary of initial tools.
        """
        # If initial_tools is provided, use it; otherwise, use an empty dictionary
        self._tools = initial_tools if initial_tools is not None else {}

    @property
    def tools(self) -> Dict[str, ITool]:
        return [self._tools[tool].as_dict() for tool in self._tools]

    def add_tools(self, tools: Dict[str, ITool]):
        """
        Add multiple tools to the toolkit.

        Parameters:
            tools (Dict[str, Tool]): A dictionary of tool objects keyed by their names.
        """
        self._tools.update(tools)

    def add_tool(self, tool: ITool):
        """
        Add a single tool to the toolkit.

        Parameters:
            tool (Tool): The tool instance to be added to the toolkit.
        """
        self._tools[tool.function['name']] = tool

    def remove_tool(self, tool_name: str):
        """
        Remove a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to be removed from the toolkit.
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def get_tool_by_name(self, tool_name: str) -> ITool:
        """
        Get a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to retrieve.

        Returns:
            Tool: The tool instance with the specified name.
        """
        if tool_name in self._tools:
            return self._tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def __len__(self) -> int:
        """
        Returns the number of tools in the toolkit.

        Returns:
            int: The number of tools in the toolkit.
        """
        return len(self._tools)
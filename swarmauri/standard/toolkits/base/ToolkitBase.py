from abc import ABC, abstractmethod
from typing import Dict, Optional
from pydantic import Field, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.toolkits.IToolkit import IToolkit
from swarmauri.core.tools.ITool import ITool  

class ToolkitBase(IToolkit, ComponentBase):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    tools: Dict[str, ITool] = {}
    resource: Optional[str] =  Field(default=ResourceTypes.TOOLKIT.value, frozen=True)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

    def list_tools(self) -> Dict[str, ITool]:
        return [self.tools[tool].as_dict() for tool in self.tools]

    def add_tools(self, tools: Dict[str, ITool]):
        """
        Add multiple tools to the toolkit.

        Parameters:
            tools (Dict[str, Tool]): A dictionary of tool objects keyed by their names.
        """
        self.tools.update(tools)

    def add_tool(self, tool: ITool):
        """
        Add a single tool to the toolkit.

        Parameters:
            tool (Tool): The tool instance to be added to the toolkit.
        """
        self.tools[tool.function['name']] = tool

    def remove_tool(self, tool_name: str):
        """
        Remove a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to be removed from the toolkit.
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
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
        if tool_name in self.tools:
            return self.tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def __len__(self) -> int:
        """
        Returns the number of tools in the toolkit.

        Returns:
            int: The number of tools in the toolkit.
        """
        return len(self.tools)
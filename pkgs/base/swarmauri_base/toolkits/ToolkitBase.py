from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Literal
from pydantic import Field, ConfigDict
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.toolkits.IToolkit import IToolkit



class ToolkitBase(IToolkit, ComponentBase):
    """
    A class representing a toolkit used by Swarm Agents.
    Tools are maintained in a dictionary keyed by the tool's name.
    """

    tools: Dict[str, SubclassUnion[ToolBase]] = {}
    resource: Optional[str] =  Field(default=ResourceTypes.TOOLKIT.value, frozen=True)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['ToolkitBase'] = 'ToolkitBase'

    def get_tools(self, 
                   include: Optional[List[str]] = None, 
                   exclude: Optional[List[str]] = None,
                   by_alias: bool = False, 
                   exclude_unset: bool = False,
                   exclude_defaults: bool = False, 
                   exclude_none: bool = False
                   ) -> Dict[str, SubclassUnion[ToolBase]]:
            """
            List all tools in the toolkit with options to include or exclude specific fields.
    
            Parameters:
                include (List[str], optional): Fields to include in the returned dictionary.
                exclude (List[str], optional): Fields to exclude from the returned dictionary.
    
            Returns:
                Dict[str, SubclassUnion[ToolBase]]: A dictionary of tools with specified fields included or excluded.
            """
            return [tool.model_dump(include=include, exclude=exclude, by_alias=by_alias,
                                   exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, 
                                    exclude_none=exclude_none) for name, tool in self.tools.items()]

    def add_tools(self, tools: Dict[str, SubclassUnion[ToolBase]]) -> None:
        """
        Add multiple tools to the toolkit.

        Parameters:
            tools (Dict[str, Tool]): A dictionary of tool objects keyed by their names.
        """
        self.tools.update(tools)

    def add_tool(self, tool: SubclassUnion[ToolBase])  -> None:
        """
        Add a single tool to the toolkit.

        Parameters:
            tool (Tool): The tool instance to be added to the toolkit.
        """
        self.tools[tool.name] = tool

    def remove_tool(self, tool_name: str) -> None:
        """
        Remove a tool from the toolkit by name.

        Parameters:
            tool_name (str): The name of the tool to be removed from the toolkit.
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found in the toolkit.")

    def get_tool_by_name(self, tool_name: str) -> SubclassUnion[ToolBase]:
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
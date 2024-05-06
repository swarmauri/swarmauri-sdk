from typing import Optional, List, Any
import json
from swarmauri.core.tools.IParameter import IParameter

class Parameter(IParameter):
    """
    A class to represent a parameter for a tool.

    Attributes:
        name (str): Name of the parameter.
        type (str): Data type of the parameter (e.g., 'int', 'str', 'float').
        description (str): A brief description of the parameter.
        required (bool): Whether the parameter is required or optional.
        enum (Optional[List[any]]): A list of acceptable values for the parameter, if any.
    """

    def __init__(self, name: str, type: str, description: str, required: bool = True, enum: Optional[List[Any]] = None):
        """
        Initializes a new instance of the Parameter class.

        Args:
            name (str): The name of the parameter.
            type (str): The type of the parameter.
            description (str): A brief description of what the parameter is used for.
            required (bool, optional): Specifies if the parameter is required. Defaults to True.
            enum (Optional[List[Any]], optional): A list of acceptable values for the parameter. Defaults to None.
        """
        self._name = name
        self._type = type
        self._description = description
        self._required = required
        self._enum = enum
        
    @property
    def name(self) -> str:
        """
        Abstract property for getting the name of the parameter.
        """
        return self._name

    @name.setter
    def name(self, value: str):
        """
        Abstract setter for setting the name of the parameter.
        """
        self._name = value

    @property
    def type(self) -> str:
        """
        Abstract property for getting the type of the parameter.
        """
        return self._type

    @type.setter
    def type(self, value: str):
        """
        Abstract setter for setting the type of the parameter.
        """
        self._type = value

    @property
    def description(self) -> str:
        """
        Abstract property for getting the description of the parameter.
        """
        return self._description

    @description.setter
    def description(self, value: str):
        """
        Abstract setter for setting the description of the parameter.
        """
        self._description = value

    @property
    def required(self) -> bool:
        """
        Abstract property for getting the required status of the parameter.
        """
        return self._required

    @required.setter
    def required(self, value: bool):
        """
        Abstract setter for setting the required status of the parameter.
        """
        self._required = value

    @property
    def enum(self) -> Optional[List[Any]]:
        """
        Abstract property for getting the enum list of the parameter.
        """
        return self._enum

    @enum.setter
    def enum(self, value: Optional[List[Any]]):
        """
        Abstract setter for setting the enum list of the parameter.
        """
        self._enum = value
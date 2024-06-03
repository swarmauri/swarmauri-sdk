from abc import ABC, abstractmethod
from typing import Optional, List, Any
from swarmauri.core.BaseComponent import BaseComponent

class ParameterBase(IParameter, BaseComponent, ABC):
    """
    An abstract class to represent a parameter for a tool.
    """
    def __init__(self, name: str, type: str, description: str, required: bool = False, enum: Optional[List[Any]] = None):
        self._name = name
        self._type = type
        self._description = description
        self._required = required
        self._enum = enum
        
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def required(self) -> bool:
        return self._required

    @required.setter
    def required(self, value: bool):
        self._required = value

    @property
    def enum(self) -> Optional[List[Any]]:
        return self._enum

    @enum.setter
    def enum(self, value: Optional[List[Any]]):
        self._enum = value
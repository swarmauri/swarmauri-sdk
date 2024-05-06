from abc import ABC
from swarmauri.core.agents.IAgentName import IAgentName


class NamedAgentBase(IAgentName, ABC):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value) -> None:
        self._name = value     
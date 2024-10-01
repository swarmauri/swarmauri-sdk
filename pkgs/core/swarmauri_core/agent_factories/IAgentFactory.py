from abc import ABC, abstractmethod
from typing import Type, Any
from datetime import datetime

class IAgentFactory(ABC):
    """
    Interface for Agent Factories, extended to include properties like ID, name, type,
    creation date, and last modification date.
    """

    @abstractmethod
    def create_agent(self, agent_type: str, **kwargs) -> Any:
        pass

    @abstractmethod
    def register_agent(self, agent_type: str, constructor: Type[Any]) -> None:
        pass

    # Abstract properties and setters
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for the factory instance."""
        pass

    @id.setter
    @abstractmethod
    def id(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the factory."""
        pass

    @name.setter
    @abstractmethod
    def name(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """Type of agents this factory produces."""
        pass

    @type.setter
    @abstractmethod
    def type(self, value: str) -> None:
        pass

    @property
    @abstractmethod
    def date_created(self) -> datetime:
        """The creation date of the factory instance."""
        pass

    @property
    @abstractmethod
    def last_modified(self) -> datetime:
        """Date when the factory was last modified."""
        pass

    @last_modified.setter
    @abstractmethod
    def last_modified(self, value: datetime) -> None:
        pass

    def __hash__(self):
        """
        The __hash__ method allows objects of this class to be used in sets and as dictionary keys.
        __hash__ should return an integer and be defined based on immutable properties.
        This is generally implemented directly in concrete classes rather than in the interface,
        but it's declared here to indicate that implementing classes must provide it.
        """
        pass

   
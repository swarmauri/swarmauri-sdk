from abc import ABC, abstractmethod

class IMessage(ABC):
    """
    An abstract interface representing a general message structure.

    This interface defines the basic attributes that all
    messages should have, including type, name, and content, 
    and requires subclasses to implement representation and formatting methods.
    """
    @property
    @abstractmethod
    def role(self) -> str:
        pass
    
    @property
    @abstractmethod
    def content(self) -> str:
        pass

    @abstractmethod
    def as_dict(self) -> dict:
        """
        An abstract method that subclasses must implement to return a dictionary representation of the object.
        """
        pass
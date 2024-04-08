from abc import ABC, abstractmethod
from swarmauri.core.messages.IMessage import IMessage

class MessageBase(IMessage, ABC):
    
    @abstractmethod
    def __init__(self, role: str, content: str):
        self._role = role
        self._content = content
    
    @property
    def role(self) -> str:
        return self._role
    
    @property
    def content(self) -> str:
        return self._content

    
    def as_dict(self) -> dict:
        """
        Dynamically return a dictionary representation of the object,
        including all properties.
        """
        result_dict = {}
        # Iterate over all attributes
        for attr in dir(self):
            # Skip private attributes and anything not considered a property
            if attr.startswith("_") or callable(getattr(self, attr)):
                continue
            result_dict[attr] = getattr(self, attr)
            
        return result_dict

    def __repr__(self) -> str:
        """
        Return the string representation of the ConcreteMessage.
        """
        return f"{self.__class__.__name__}(role='{self.role}')"
    
    def __getattr__(self, name):
        """
        Return the value of the named attribute of the instance.
        """
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    
    def __setattr__(self, name, value):
        """
        Set the value of the named attribute of the instance.
        """
        self.__dict__[name] = value
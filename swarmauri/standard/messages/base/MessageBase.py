from abc import ABC, abstractmethod
from pydantic import PrivateAttr, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.messages.IMessage import IMessage

class MessageBase(IMessage, ComponentBase, ABC):
    content: str
    _role: str = PrivateAttr()
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.MESSAGE.value, frozen=True)
    
    @property
    def role(self) -> str:
        return self._role
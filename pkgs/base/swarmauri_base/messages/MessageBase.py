from typing import Optional, Literal, List, Dict, Union
from pydantic import ConfigDict, Field
from swarmauri_core.messages.IMessage import IMessage
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class MessageBase(IMessage, ComponentBase):
    content: Union[str, List[Dict]]
    role: str
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    resource: Optional[str] = Field(default=ResourceTypes.MESSAGE.value, frozen=True)
    type: Literal["MessageBase"] = "MessageBase"

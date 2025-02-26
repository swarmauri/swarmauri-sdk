import warnings

from typing import Optional, Literal, Union, List
from pydantic import Field, BaseModel, ConfigDict

from swarmauri_standard.messages.HumanMessage import contentItem
from swarmauri_base.messages.MessageBase import MessageBase
from swarmauri_base.ComponentBase import ComponentBase


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



class UsageData(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    prompt_time: Optional[float] = None
    completion_time: Optional[float] = None
    total_time: Optional[float] = None
    model_config = ConfigDict(extra="allow")


@ComponentBase.register_type(MessageBase, "AgentMessage")
class AgentMessage(MessageBase):
    content: Optional[Union[str, List[contentItem]]] = None
    role: str = Field(default="assistant")
    # tool_calls: Optional[Any] = None
    name: Optional[str] = None
    type: Literal["AgentMessage"] = "AgentMessage"
    usage: Optional[UsageData] = None

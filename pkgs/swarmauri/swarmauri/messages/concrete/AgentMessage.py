from typing import Optional, Any, Literal, Union, List
from pydantic import Field, BaseModel, ConfigDict
from swarmauri.messages.base.MessageBase import MessageBase

from swarmauri.messages.concrete.HumanMessage import contentItem


class UsageData(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    prompt_time: Optional[float] = None
    completion_time: Optional[float] = None
    total_time: Optional[float] = None

    model_config = ConfigDict(extra="allow")


class AgentMessage(MessageBase):
    content: Optional[Union[str, List[contentItem]]] = None
    role: str = Field(default="assistant")
    # tool_calls: Optional[Any] = None
    name: Optional[str] = None
    type: Literal["AgentMessage"] = "AgentMessage"
    usage: Optional[UsageData] = None

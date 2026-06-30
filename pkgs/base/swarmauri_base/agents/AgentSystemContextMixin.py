from typing import Union
from pydantic import BaseModel, ConfigDict, field_validator

from swarmauri_core.agents.IAgentSystemContext import IAgentSystemContext
from swarmauri_core.messages.IMessage import IMessage
from swarmauri_base.messages.MessageBase import MessageBase


class AgentSystemContextMixin(IAgentSystemContext, BaseModel):
    system_context: Union[IMessage, str]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("system_context", mode="before")
    def set_system_context(cls, value: Union[str, IMessage]) -> IMessage:
        if isinstance(value, str):
            return MessageBase(content=value, role="system")
        return value

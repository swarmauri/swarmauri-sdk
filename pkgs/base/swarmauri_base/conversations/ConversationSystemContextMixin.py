from typing import Optional
from pydantic import BaseModel, ConfigDict

from swarmauri_core.conversations.ISystemContext import ISystemContext
from swarmauri_core.messages.IMessage import IMessage


class ConversationSystemContextMixin(ISystemContext, BaseModel):
    system_context: Optional[IMessage]
    model_config = ConfigDict(arbitrary_types_allowed=True)

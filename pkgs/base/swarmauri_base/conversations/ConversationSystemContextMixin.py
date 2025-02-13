from typing import Optional
from pydantic import BaseModel

from swarmauri_core.conversations.ISystemContext import ISystemContext
from swarmauri_standard.messages.SystemMessage import SystemMessage


class ConversationSystemContextMixin(ISystemContext, BaseModel):
    system_context: Optional[SystemMessage]

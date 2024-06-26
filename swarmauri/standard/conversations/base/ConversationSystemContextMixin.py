from abc import ABC
from typing import Optional, Literal
from pydantic import BaseModel
from swarmauri.core.conversations.ISystemContext import ISystemContext
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

class ConversationSystemContextMixin(ISystemContext, BaseModel):
    system_context: Optional[SystemMessage]

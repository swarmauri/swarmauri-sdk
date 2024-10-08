from abc import ABC
from typing import Optional, Literal
from pydantic import BaseModel
from swarmauri_core.conversations.ISystemContext import ISystemContext
from swarmauri.messages.concrete.SystemMessage import SystemMessage

class ConversationSystemContextMixin(ISystemContext, BaseModel):
    system_context: Optional[SystemMessage]

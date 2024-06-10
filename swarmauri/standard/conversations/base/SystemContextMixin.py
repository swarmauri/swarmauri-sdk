from abc import ABC
from typing import Optional
from swarmauri.core.conversations.ISystemContext import ISystemContext
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class SystemContextMixin(ISystemContext, ConversationBase, ABC):
    system_context: Optional[SystemMessage]

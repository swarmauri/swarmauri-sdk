from typing import Optional, Union, List, Literal
from pydantic import Field, ConfigDict
from collections import deque
from swarmauri_core.messages.IMessage import IMessage
from swarmauri_core.conversations.IMaxSize import IMaxSize
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.conversations.ConversationSystemContextMixin import ConversationSystemContextMixin
from swarmauri_standard.messages.SystemMessage import SystemMessage
from swarmauri_standard.exceptions.IndexErrorWithContext import IndexErrorWithContext


class SessionCacheConversation(IMaxSize, ConversationSystemContextMixin, ConversationBase):
    max_size: int = Field(default=2, gt=1)
    system_context: Optional[SystemMessage] = None
    session_max_size: int = Field(default=-1)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['SessionCacheConversation'] = 'SessionCacheConversation'

    def __init__(self, **data):
        super().__init__(**data)
        if self.session_max_size == -1:
            self.session_max_size = self.max_size

    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and ensures history does not exceed the max size.
        This only allows system context to be set through the system context method.
        We are forcing the SystemContext to be a preamble only.
        """
        if isinstance(message, SystemMessage):
            raise ValueError(f"System context cannot be set through this method on {self.__class_name__}.")
        if not self._history and not isinstance(message, HumanMessage):
            raise ValueError("The first message in the history must be an HumanMessage.")
        if self._history and isinstance(self._history[-1], HumanMessage) and isinstance(message, HumanMessage):
            raise ValueError("Cannot have two repeating HumanMessages.")
        
        super().add_message(message)


    def session_to_dict(self) -> List[dict]:
        """
        Converts session messages to a list of dictionaries.
        """
        included_fields = {"role", "content"}
        return [message.dict(include=included_fields) for message in self.session]
    
    @property
    def session(self) -> List[IMessage]:
        return self._history[-self.session_max_size:]

    @property
    def history(self):
        res = []
        if not self._history or self.max_size == 0:
            if self.system_context:
                return [self.system_context]
            else:
                return []

        # Initialize alternating with the expectation to start with HumanMessage
        alternating = True
        count = 0

        for message in self._history[-self.max_size:]:
            if isinstance(message, HumanMessage) and alternating:
                res.append(message)
                alternating = not alternating  # Switch to expecting AgentMessage
                count += 1
            elif isinstance(message, AgentMessage) and not alternating:
                res.append(message)
                alternating = not alternating  # Switch to expecting HumanMessage
                count += 1

            if count >= self.max_size:
                break
                
        if self.system_context:
            res = [self.system_context] + res
            
        return res


from typing import Optional, Union, List, Literal
from pydantic import Field, ConfigDict, field_validator
from swarmauri_core.messages.IMessage import IMessage
from swarmauri_core.conversations.IMaxSize import IMaxSize
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.conversations.ConversationSystemContextMixin import ConversationSystemContextMixin
from swarmauri_standard.messages.SystemMessage import SystemMessage
from swarmauri_standard.exceptions.IndexErrorWithContext import IndexErrorWithContext

class MaxSystemContextConversation(IMaxSize, ConversationSystemContextMixin, ConversationBase):
    system_context: Optional[SystemMessage] = SystemMessage(content="")
    max_size: int = Field(default=2, gt=1)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['MaxSystemContextConversation'] = 'MaxSystemContextConversation'
    
    @field_validator('system_context', mode='before')
    def set_system_context(cls, value: Union[str, SystemMessage]) -> SystemMessage:
        if isinstance(value, str):
            return SystemMessage(content=value)
        return value
    
    @property
    def history(self) -> List[IMessage]:
        """
        Get the conversation history, ensuring it starts with a 'user' message and alternates correctly between 'user' and 'assistant' roles.
        The maximum number of messages returned does not exceed max_size + 1.
        """
        res = []  # Start with an empty list to build the proper history

        # Attempt to find the first 'user' message in the history.
        user_start_index = -1
        for index, message in enumerate(self._history):
            if isinstance(message, HumanMessage):  # Identify user message
                user_start_index = index
                break

        # If no 'user' message is found, just return the system context.
        if user_start_index == -1:
            return [self.system_context]

        # Build history from the first 'user' message ensuring alternating roles.
        res.append(self.system_context)
        alternating = True
        count = 0 
        for message in self._history[user_start_index:]:
            if count > self.max_size: # max size
                break
            if alternating and isinstance(message, HumanMessage) or not alternating and isinstance(message, AgentMessage):
                res.append(message)
                alternating = not alternating
                count += 1
            elif not alternating and isinstance(message, HumanMessage):
                # If we find two 'user' messages in a row when expecting an 'assistant' message, we skip this 'user' message.
                continue
            else:
                # If there is no valid alternate message to append, break the loop
                break

        return res

    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and ensures history does not exceed the max size.
        """
        if isinstance(message, SystemMessage):
            raise ValueError(f"System context cannot be set through this method on {self.__class_name__}.")
        elif isinstance(message, IMessage):
            self._history.append(message)
        else:
            raise ValueError(f"Must use a subclass of IMessage")
        self._enforce_max_size_limit()
        
    def _enforce_max_size_limit(self):
        """
        Remove messages from the beginning of the conversation history if the limit is exceeded.
        We add one to max_size to account for the system context message
        """
        try:
            while len(self._history) > self.max_size + 1:
                self._history.pop(0)
                self._history.pop(0)
        except IndexError as e:
            raise IndexErrorWithContext(e)

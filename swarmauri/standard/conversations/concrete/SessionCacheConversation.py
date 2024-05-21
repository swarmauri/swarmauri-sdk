from typing import Optional, Union, List
from collections import deque
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize
from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.messages.concrete import SystemMessage, AgentMessage, HumanMessage
from swarmauri.standard.exceptions.concrete import IndexErrorWithContext

class SessionCacheConversation(SystemContextBase, IMaxSize):
    def __init__(self, max_size: int = 2, 
        system_message_content: Optional[SystemMessage] = None, 
        session_cache_max_size: int = -1):
        """
        Initializes the conversation with a system context message and a maximum history size. Also initializes the conversation with
        a session cache with its own maximum size.

        Parameters:
            max_size (int): The maximum number of messages allowed in the conversation history.
            system_message_content (Optional[str], optional): The initial system message content. Can be a string.
            session_cache_max_size (int): The maximum number of messages allowed in the session cache.
        """
        SystemContextBase.__init__(self, system_message_content=system_message_content if system_message_content else "")
        self._max_size = max_size  # Set the maximum size
        if session_cache_max_size:
            self._session_cache_max_size = session_cache_max_size
        else:
            self._session_cache_max_size = self._max_size
        self._history = []

    @property
    def session_cache_max_size(self) -> int:
        return self._session_cache_max_size

    @property
    def max_size(self) -> int:
        return self._max_size

    @max_size.setter
    def max_size(self, new_max_size: int) -> None:
        if new_max_size <= 0:
            raise ValueError("max_size must be greater than 0.")
        self._max_size = new_max_size

    @session_cache_max_size.setter
    def session_cache_max_size(self, new_max_cache_size: int) -> None:
        if new_max_cache_size <= 0:
            raise ValueError("session_cache_max_size must be greater than 0.")
        self._session_cache_max_size = new_max_cache_size

    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and ensures history does not exceed the max size.
        This only allows system context to be set through the system context method.
        We are forcing the SystemContext to be a preamble only.
        """
        if isinstance(message, SystemMessage):
            raise ValueError(f"System context cannot be set through this method on {self.__class_name__}.")
        else:
            super().add_message(message)

    @property
    def history(self) -> List[IMessage]:
        """
        Retrieves the conversation history, ensuring it starts with the system message and alternates correctly.
        """
        if not self._history:
            return [self._system_context]

        # Initialize the response starting with the system context
        res = [self._system_context]
        max_history_length = self._max_size

        # Scan for alternating messages starting from the last 'user' message
        last_user_index = None
        for i in range(len(self._history) - 1, -1, -1):
            if isinstance(self._history[i], HumanMessage):
                last_user_index = i
                break

        if last_user_index is not None:
            alternating = True  # True if expecting HumanMessage, False for AgentMessage
            for message in reversed(self._history[max(0, last_user_index - self._max_size * 2):last_user_index + 1]):
                if len(res) >= max_history_length:
                    break
                if (alternating and isinstance(message, HumanMessage)) or (not alternating and isinstance(message, AgentMessage)):
                    res.append(message)
                    alternating = not alternating

        # Return the conversation history starting from the oldest to newest, excluding the system context for reordering
        return [res[0]] + list(reversed(res[1:]))

    def session_to_dict(self) -> List[dict]:
        """
        Converts session messages to a list of dictionaries.
        """
        return [message.as_dict() for message in self.session]

    @property
    def session(self) -> List[IMessage]:
        return self._history[-self._session_cache_max_size:]

    @property
    def system_context(self) -> Union[SystemMessage, None]:
        """Get the system context message. Raises an error if it's not set."""
        if self._system_context is None:
            raise ValueError("System context has not been set.")
        return self._system_context

    @system_context.setter
    def system_context(self, new_system_message: Union[SystemMessage, str]) -> None:
        """
        Set a new system context message. The new system message can be a string or 
        an instance of SystemMessage. If it's a string, it converts it to a SystemMessage.
        """
        if isinstance(new_system_message, SystemMessage):
            self._system_context = new_system_message
        elif isinstance(new_system_message, str):
            self._system_context = SystemMessage(new_system_message)
        else:
            raise ValueError("System context must be a string or a SystemMessage instance.")
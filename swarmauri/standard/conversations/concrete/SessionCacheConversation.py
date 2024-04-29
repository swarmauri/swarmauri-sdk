from typing import Optional, Union, List
from collections import deque
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.conversations.IMaxSize import IMaxSize
from swarmauri.standard.conversations.base.SystemContextBase import SystemContextBase
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage
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
            session_cache_max_size (int): The maximum number of messages allowed in the session cache.
            system_message_content (Optional[str], optional): The initial system message content. Can be a string.
        """
        SystemContextBase.__init__(self, system_message_content=system_message_content if system_message_content else "")  # Initialize SystemContext with a SystemMessage
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
        self._history.append(message)

    @property
    def history(self) -> List[IMessage]:
        res = [] 
        res.append(self.system_context)
        res.extend(self._history[-self._max_size:])
        return res

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
        self.add_message()
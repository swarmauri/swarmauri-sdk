from typing import Literal, Optional, Any
from logging import Logger, getLogger
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.ComponentBase import ComponentBase

@ComponentBase.register_type(ConversationBase, "SessionContextConv")
class SessionContextConv(ConversationBase, ComponentBase):
    """
    Concrete implementation managing session context for conversations.
    Handles session data storage and retrieval.
    """
    
    type: Literal["SessionContextConv"] = "SessionContextConv"
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialize SessionContextConv with optional logger.
        
        Args:
            logger: Optional logger instance. Defaults to None.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.session_context = {}
        self.logger.info("Initialized SessionContextConv")
    
    def store(self, key: str, value: Any) -> None:
        """
        Store key-value pair in session context.
        
        Args:
            key: Key for storing value
            value: Value to store
        """
        self.session_context[key] = value
        self.logger.info(f"Stored value with key: {key}")
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve value from session context by key.
        
        Args:
            key: Key to retrieve value
        Returns:
            Value if key exists, else None
        """
        value = self.session_context.get(key)
        self.logger.info(f"Retrieved value for key: {key}" + 
                        (f" found: {value}" if value is not None else " not found"))
        return value
    
    def update(self, key: str, value: Any) -> None:
        """
        Update value in session context by key.
        
        Args:
            key: Key for updating value
            value: New value to set
        """
        if key in self.session_context:
            self.session_context[key] = value
            self.logger.info(f"Updated value for key: {key}")
        else:
            self.logger.warning(f"Key: {key} not found in session context")
    
    def clear(self, key: str) -> None:
        """
        Remove key from session context.
        
        Args:
            key: Key to remove
        """
        if key in self.session_context:
            del self.session_context[key]
            self.logger.info(f"Cleared key: {key}")
        else:
            self.logger.warning(f"Key: {key} not found in session context")
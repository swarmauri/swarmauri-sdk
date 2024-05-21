from typing import List, Union
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class SimpleConversation(ConversationBase):
    """
    Concrete implementation of IConversation, managing conversation history and operations.
    """
    
    def __init__(self):
       super().__init__()
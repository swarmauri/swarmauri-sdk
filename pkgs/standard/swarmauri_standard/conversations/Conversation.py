from typing import Literal
from swarmauri_base.conversations.ConversationBase import ConversationBase

class Conversation(ConversationBase):
    """
    Concrete implementation of ConversationBase, managing conversation history and operations.
    """    
    type: Literal['Conversation'] = 'Conversation'
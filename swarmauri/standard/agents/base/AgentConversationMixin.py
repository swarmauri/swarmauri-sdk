from pydantic import BaseModel, ConfigDict, field_validator
from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.core.conversations.IConversation import IConversation

class AgentConversationMixin(IAgentConversation, BaseModel):
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    conversation: IConversation

    @field_validator('conversation')
    @classmethod
    def check_conversation_type(cls, value):
        if not isinstance(value, IConversation):
            raise TypeError('model must be an instance of IConversation or its subclass')
        return value
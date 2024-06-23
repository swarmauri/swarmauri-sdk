from pydantic import BaseModel, ConfigDict, field_validator
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class AgentConversationMixin(IAgentConversation, BaseModel):
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    conversation: SubclassUnion[ConversationBase]
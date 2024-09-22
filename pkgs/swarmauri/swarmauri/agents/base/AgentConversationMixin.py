from pydantic import BaseModel, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.agents.IAgentConversation import IAgentConversation
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase

class AgentConversationMixin(IAgentConversation, BaseModel):
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
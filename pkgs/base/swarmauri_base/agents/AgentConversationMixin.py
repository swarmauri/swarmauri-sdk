from pydantic import BaseModel, ConfigDict
from swarmauri_core.typing import SubclassUnion
from swarmauri_core.agents.IAgentConversation import IAgentConversation
from swarmauri_base.conversations.ConversationBase import ConversationBase

class AgentConversationMixin(IAgentConversation, BaseModel):
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
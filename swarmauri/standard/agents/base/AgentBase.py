from typing import Any, Optional, Dict, Union, Literal
from pydantic import ConfigDict, Field, field_validator
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.standard.llms.base.LLMBase import LLMBase
from swarmauri.standard.conversations.base.ConversationBase import ConversationBase # 🚧  Placeholder

class AgentBase(IAgent, ComponentBase):
    llm: SubclassUnion[LLMBase]
    conversation: SubclassUnion[ConversationBase] # 🚧  Placeholder
    resource: ResourceTypes =  Field(default=ResourceTypes.AGENT.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['AgentBase'] = 'AgentBase'

    def exec(self, input_str: Optional[Union[str, IMessage]] = "", llm_kwargs: Optional[Dict] = {}) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
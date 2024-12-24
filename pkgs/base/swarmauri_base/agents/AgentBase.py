from typing import Any, Optional, Dict, Union, Literal
from pydantic import ConfigDict, Field, field_validator
from swarmauri_core.typing import SubclassUnion
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.messages.IMessage import IMessage
from swarmauri_core.agents.IAgent import IAgent
from swarmauri_base.llms.LLMBase import LLMBase

class AgentBase(IAgent, ComponentBase):
    llm: SubclassUnion[LLMBase]
    resource: ResourceTypes =  Field(default=ResourceTypes.AGENT.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['AgentBase'] = 'AgentBase'

    def exec(self, input_str: Optional[Union[str, IMessage]] = "", llm_kwargs: Optional[Dict] = {}) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
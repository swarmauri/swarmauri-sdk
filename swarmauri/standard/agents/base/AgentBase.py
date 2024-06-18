from typing import Any, Optional, Dict, Union
from pydantic import ConfigDict, Field, field_validator
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.messages.IMessage import IMessage
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.llms.IPredict import IPredict

class AgentBase(IAgent, ComponentBase):
    llm: IPredict
    resource: ResourceTypes =  Field(default=ResourceTypes.AGENT.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

    @field_validator('llm')
    @classmethod
    def check_model_type(cls, value):
        if not isinstance(value, IPredict):
            raise TypeError('model must be an instance of IPredict or its subclass')
        return value

    def exec(self, input_str: Optional[Union[str, IMessage]] = "", llm_kwargs: Optional[Dict] = {}) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
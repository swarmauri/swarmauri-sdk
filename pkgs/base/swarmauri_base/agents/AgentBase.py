from typing import Any, Optional, Dict, Union, Literal
from pydantic import ConfigDict, Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes, SubclassUnion
from swarmauri_core.messages.IMessage import IMessage
from swarmauri_core.agents.IAgent import IAgent
from swarmauri_base.llms.LLMBase import LLMBase


@ComponentBase.register_model()
class AgentBase(IAgent, ComponentBase):
    llm: SubclassUnion[LLMBase]
    llm_kwargs: Optional[Dict] = {}
    resource: ResourceTypes = Field(default=ResourceTypes.AGENT.value)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["AgentBase"] = "AgentBase"

    def exec(
        self,
        input_str: Optional[Union[str, IMessage]] = "",
        llm_kwargs: Optional[Dict] = {},
    ) -> Any:
        raise NotImplementedError(
            "The `exec` function has not been implemented on this class."
        )

    async def aexec(
        self,
        input_str: Optional[Union[str, IMessage]] = "",
        llm_kwargs: Optional[Dict] = {},
    ) -> Any:
        raise NotImplementedError(
            "The `aexec` function has not been implemented on this class."
        )

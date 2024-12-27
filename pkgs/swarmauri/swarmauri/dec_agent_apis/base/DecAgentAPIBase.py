from typing import Any, Dict, Literal

from pydantic import ConfigDict, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.dec_agent_apis.IDecAgentAPI import IDecAgentAPI


class DecAgentAPIBase(IDecAgentAPI, ComponentBase):
    resource: ResourceTypes = Field(default=ResourceTypes.DEC_AGENT_API.value)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["DecAgentAPIBase"] = "DecAgentAPIBase"

    def send_message(self, message: Dict[str, Any]) -> None:
        """
        Sends a message to the DecAgent.
        """
        raise NotImplementedError("Method not implemented")

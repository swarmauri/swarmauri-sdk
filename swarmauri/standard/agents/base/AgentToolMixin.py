from pydantic import BaseModel, ConfigDict
from swarmauri.core.agents.IAgentToolkit import IAgentToolkit
from swarmauri.core.toolkits.IToolkit import IToolkit

class AgentToolMixin(IAgentToolkit, BaseModel):
    toolkit: IToolkit
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    
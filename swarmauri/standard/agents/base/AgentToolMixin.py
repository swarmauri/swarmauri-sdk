from pydantic import BaseModel
from swarmauri.core.agents.IAgentToolkit import IAgentToolkit
from swarmauri.core.toolkits.IToolkit import IToolkit


class AgentToolMixin(IAgentToolkit, BaseModel):
    toolkit: IToolkit
    
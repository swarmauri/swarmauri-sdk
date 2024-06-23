from pydantic import BaseModel, ConfigDict
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.agents.IAgentToolkit import IAgentToolkit
from swarmauri.standard.toolkits.base.ToolkitBase import ToolkitBase

class AgentToolMixin(IAgentToolkit, BaseModel):
    toolkit: SubclassUnion[ToolkitBase]
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    
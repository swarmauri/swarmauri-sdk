from pydantic import BaseModel, ConfigDict

from swarmauri_core.agents.IAgentToolkit import IAgentToolkit
from swarmauri_core.ComponentBase import SubclassUnion
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase


class AgentToolMixin(IAgentToolkit, BaseModel):
    toolkit: SubclassUnion[ToolkitBase]
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

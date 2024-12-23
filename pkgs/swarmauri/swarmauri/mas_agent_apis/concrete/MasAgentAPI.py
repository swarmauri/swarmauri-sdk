from typing import Literal
from swarmauri.mas_agent_apis.base.MasAgentAPIBase import MasAgentAPIBase


class MasAgentAPI(MasAgentAPIBase):
    """Concrete implementation of MAS-specific agent-local APIs."""

    type: Literal["MasAgentAPI"] = "MasAgentAPI"

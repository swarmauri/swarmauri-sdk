from typing import Literal
from swarmauri.agent_apis.base.AgentAPIBase import AgentAPIBase


class AgentAPI(AgentAPIBase):
    """
    Concrete implementation of the AgentAPIBase.
    """

    type: Literal["AgentAPI"] = "AgentAPI"

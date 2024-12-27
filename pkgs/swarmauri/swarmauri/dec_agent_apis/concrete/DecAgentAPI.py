from typing import Literal
from swarmauri.dec_agent_apis.base.DecAgentAPIBase import DecAgentAPIBase


class DecAgentAPI(DecAgentAPIBase):
    """
    Concrete implementation of DecAgentAPI, managing agent-local APIs.
    """

    type: Literal["DecAgentAPI"] = "DecAgentAPI"

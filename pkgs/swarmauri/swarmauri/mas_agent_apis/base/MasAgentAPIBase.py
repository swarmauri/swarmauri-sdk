from typing import Any, Literal, Optional

from pydantic import ConfigDict, Field
from swarmauri_core.ComponentBase import ResourceTypes, ComponentBase
from swarmauri_core.mas_agent_apis.IMasAgentAPI import IMasAgentAPI
from swarmauri.transports.base.TransportBase import TransportBase
from swarmauri_core.typing import SubclassUnion


class MasAgentAPIBase(IMasAgentAPI, ComponentBase):
    """Base implementation of the MAS-specific agent-local APIs."""

    transport: SubclassUnion[TransportBase]
    resource: Optional[str] = Field(default=ResourceTypes.MAS_AGENT_API.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["MasAgentAPIBase"] = "MasAgentAPIBase"

    def send_message(self, message: Any, recipient_id: str) -> None:
        """Send a message to a specific recipient."""
        self.transport.send(sender=self, message=message, recipient=recipient_id)

    def subscribe(self, topic: str) -> None:
        """Subscribe to a topic."""
        self.transport.subscribe(topic)

    def publish(self, topic: str) -> None:
        """Publish a message to a topic"""
        self.transport.publish(topic)

from abc import abstractmethod
from typing import Any, Dict, Literal, Optional

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.publishers.IPublish import IPublish


@ComponentBase.register_model()
class PublishBase(IPublish, ComponentBase):
    """Abstract base class implementing the :class:`IPublish` interface."""

    resource: Optional[str] = Field(default=ResourceTypes.PUBLISHER.value, frozen=True)
    type: Literal["PublishBase"] = "PublishBase"

    @abstractmethod
    def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """Publish ``payload`` to ``channel``."""
        raise NotImplementedError("publish() not implemented in subclass yet.")

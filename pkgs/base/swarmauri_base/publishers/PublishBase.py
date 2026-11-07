from abc import abstractmethod
from typing import Any, Literal

from pydantic import Field
from swarmauri_core.publishers.IPublish import IPublish

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class PublishBase(IPublish, ComponentBase):
    """Abstract base class implementing the :class:`IPublish` interface."""

    resource: str | None = Field(
        default=ResourceTypes.PUBLISHER.value, frozen=True
    )
    type: Literal["PublishBase"] = "PublishBase"

    @abstractmethod
    def publish(self, channel: str, payload: dict[str, Any]) -> None:
        """Publish ``payload`` to ``channel``."""
        raise NotImplementedError("publish() not implemented in subclass yet.")

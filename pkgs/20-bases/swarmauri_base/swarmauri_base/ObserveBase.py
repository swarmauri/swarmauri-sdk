"""Base class for observable SwarmAuri components."""

from typing import (
    ClassVar,
    Literal,
    TypeVar,
)

from pydantic import ConfigDict

from swarmauri_base.DynamicBase import DynamicBase
from swarmauri_base.ServiceMixin import ServiceMixin
from swarmauri_base.YamlMixin import YamlMixin

T = TypeVar("T", bound="ObserveBase")


@DynamicBase.register_type()
class ObserveBase(YamlMixin, ServiceMixin, DynamicBase):
    """
    Base class for all components.
    """

    _type: ClassVar[str] = "ObserveBase"

    # Instance-attribute type (to support deserialization)
    type: Literal["ObserveBase"] = "ObserveBase"
    name: str | None = None
    version: str = "0.1.0"

    model_config = ConfigDict(arbitrary_types_allowed=True)

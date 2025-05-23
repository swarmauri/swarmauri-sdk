"""Base class for observable SwarmAuri components."""

from typing import (
    ClassVar,
    Literal,
    Optional,
    TypeVar,
)

from pydantic import ConfigDict
from swarmauri_base.YamlMixin import YamlMixin
from swarmauri_base.ServiceMixin import ServiceMixin
from swarmauri_base.DynamicBase import DynamicBase

T = TypeVar("T", bound="ObserveBase")


@DynamicBase.register_type()
class ObserveBase(YamlMixin, ServiceMixin, DynamicBase):
    """
    Base class for all components.
    """

    _type: ClassVar[str] = "ObserveBase"

    # Instance-attribute type (to support deserialization)
    type: Literal["ObserveBase"] = "ObserveBase"
    name: Optional[str] = None
    version: str = "0.1.0"

    model_config = ConfigDict(arbitrary_types_allowed=True)

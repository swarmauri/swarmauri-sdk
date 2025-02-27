# swarmauri_base/ObserveBase.py

from typing import (
    ClassVar,
    List,
    Literal,
    Optional,
    TypeVar,
)
from uuid import uuid4

from pydantic import Field, ConfigDict

###########################################
# Logging
###########################################

###########################################
# Typing
###########################################

T = TypeVar("T", bound="ObserveBase")


###########################################
# ObserveBase
###########################################

def generate_id() -> str:
    return str(uuid4())

from swarmauri_base.YamlMixin import YamlMixin
from swarmauri_base.DynamicBase import DynamicBase

@DynamicBase.register_type()
class ObserveBase(YamlMixin, DynamicBase):
    """
    Base class for all components.
    """
    _type: ClassVar[str] = "ObserveBase"

    # Instance-attribute type (to support deserialization)
    type: Literal["ObserveBase"] = "ObserveBase"
    name: Optional[str] = None
    id: str = Field(default_factory=generate_id)
    members: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    host: Optional[str] = None
    version: str = "0.1.0"

    model_config = ConfigDict(arbitrary_types_allowed=True)


    

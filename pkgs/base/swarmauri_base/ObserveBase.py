# swarmauri_base/ObserveBase.py

from typing import (
    Annotated,
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator, ConfigDict

###########################################
# Logging
###########################################
from .glogging import glogger

###########################################
# Typing
###########################################

T = TypeVar("T", bound="ObserveBase")


###########################################
# ObserveBase
###########################################

def generate_id() -> str:
    return str(uuid4())

from .YamlMixin import YamlMixin
from .DynamicBase import DynamicBase

@DynamicBase.register_type()
class ObserveBase(YamlMixin, DynamicBase, BaseModel):
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


    

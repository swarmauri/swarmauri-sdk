from uuid import uuid4

from pydantic import BaseModel, Field
from typing import Optional, List
from swarmauri_base.DynamicBase import DynamicBase


def generate_id() -> str:
    return str(uuid4())


@DynamicBase.register_model()
class ServiceMixin(BaseModel):
    # Class-level default logger is now a FullUnion[LoggerBase] instance.
    id: str = Field(default_factory=generate_id)
    members: Optional[List[str]] = None
    owners: Optional[List[str]] = None
    host: Optional[str] = None

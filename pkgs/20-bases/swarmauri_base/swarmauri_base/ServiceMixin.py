"""Mixin providing service metadata fields."""

from uuid import uuid4

from pydantic import BaseModel, Field

from swarmauri_base.DynamicBase import DynamicBase


def generate_id() -> str:
    """Return a new unique identifier."""

    return str(uuid4())


@DynamicBase.register_model()
class ServiceMixin(BaseModel):
    """Attach service-related metadata fields to a model."""

    # Class-level default logger is now a FullUnion[LoggerBase] instance.
    id: str = Field(default_factory=generate_id)
    members: list[str] | None = None
    owners: list[str] | None = None
    host: str | None = None

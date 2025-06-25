import uuid
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, func

Base = declarative_base()


class UUIDMixin:
    """Provides a UUID primary key column."""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """Provides creation and last-modified timestamps."""
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Base class for all ORM models with standard ID and timestamps."""
    __abstract__ = True
